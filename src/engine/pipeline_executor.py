import time

from config.loader import Config
from engine.action_registry import ACTION_REGISTRY
from engine_reader.pipeline_reader import PipelineReader
from quay.quay_gateway import QuayGateway
from utils.display import Display, PipelineStats, StepResult
from utils.logger import Logger as log


class PipelineExecutor:

    def __init__(self):
        self.reader = PipelineReader()
        self.cfg = Config()
        self.stats = PipelineStats()
        self.gateway = QuayGateway()

    def run_pipeline(self, pipeline, inputs_file):
        inputs = self.reader.load_inputs(inputs_file)

        Display.inputs_overview(inputs, debug=self.cfg.debug)

        # Count total enabled steps
        enabled_steps = [s for s in pipeline.pipeline if s.enabled]
        self.stats.total_steps = len(enabled_steps)
        self.stats.skipped_steps = len(pipeline.pipeline) - len(enabled_steps)

        step_num = 0
        for step in pipeline.pipeline:
            step_num += 1
            if not step.enabled:
                Display.step_skipped(step_num, self.stats.total_steps + self.stats.skipped_steps, step.name)
                continue

            action_class = ACTION_REGISTRY.get(step.job)
            if action_class is None:
                raise ValueError(f"Unknown job type: '{step.job}'. Check ACTION_REGISTRY.")
            action = action_class(gateway=self.gateway)

            # Show step start
            Display.step_start(
                step_num - self.stats.skipped_steps,
                self.stats.total_steps,
                step.name,
                step.job
            )
            step_start_time = time.time()

            if step.params_list:
                key = step.params_list.replace("{{ ", "").replace(" }}", "")
                items = inputs.get(key, [])

                if self.cfg.debug:
                    log.debug("PipelineExecutor", f"Dynamic params for '{key}': {len(items)} items")

                if not isinstance(items, list):
                    log.error("PipelineExecutor",
                              f"Invalid params list for key='{key}'. Expected list, got: {type(items)}")
                    raise ValueError(f"Invalid params list for key='{key}'")

                all_success = True
                for index, params in enumerate(items):
                    try:
                        Display.dynamic_iteration(index + 1, len(items), params)

                        if self.cfg.debug:
                            log.debug("PipelineExecutor",
                                      f"[{step.name}] Executing dynamic iteration {index + 1}/{len(items)} with params={params}")

                        if not isinstance(params, dict):
                            log.error(
                                "PipelineExecutor",
                                f"Iteration {index + 1}: expected dict but received {type(params)} – value={params}"
                            )
                            raise ValueError(f"Invalid params in dynamic list for step '{step.name}'")

                        response = action.execute(params)
                        Display.dynamic_iteration_result(response.success)

                        if not response.success:
                            all_success = False
                            log.error("PipelineExecutor", f"Iteration {index + 1} failed: {response.message}")

                    except Exception as ex:
                        Display.dynamic_iteration_result(False)
                        log.error("PipelineExecutor",
                                  f"Exception while executing step '{step.name}' with dynamic params: {ex}")
                        step_duration = time.time() - step_start_time
                        self.stats.add_result(StepResult(step.name, step.job, False, str(ex), step_duration))
                        raise

                step_duration = time.time() - step_start_time
                self.stats.add_result(StepResult(step.name, step.job, all_success, None, step_duration))
                Display.step_result(all_success, None, step_duration)

                if not all_success:
                    raise RuntimeError(f"Step '{step.name}' failed during dynamic iteration")

                continue

            if self.cfg.debug:
                log.debug("PipelineExecutor", f"Executing step {step.name} with params: {step.params or {} }")

            try:
                response = action.execute(step.params or {})
                step_duration = time.time() - step_start_time

                self.stats.add_result(StepResult(
                    step.name, step.job, response.success, response.message, step_duration
                ))
                Display.step_result(response.success, response.message, step_duration)

                if not response.success:
                    raise RuntimeError(f"Step '{step.name}' failed: {response.message}")

            except Exception as ex:
                step_duration = time.time() - step_start_time
                if step.name not in [r.name for r in self.stats.results]:
                    self.stats.add_result(StepResult(step.name, step.job, False, str(ex), step_duration))
                    Display.step_result(False, str(ex), step_duration)
                raise
