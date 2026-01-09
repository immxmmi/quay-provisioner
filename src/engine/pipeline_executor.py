from config.loader import Config
from engine.action_registry import ACTION_REGISTRY
from engine_reader.pipeline_reader import PipelineReader
from utils.logger import Logger as log


class PipelineExecutor:

    def __init__(self):
        self.reader = PipelineReader()
        self.cfg = Config()

    def run_pipeline(self, pipeline, inputs_file):
        inputs = self.reader.load_inputs(inputs_file)

        if self.cfg.debug:
            log.debug("PipelineExecutor", f"Executor loaded inputs: {inputs}")

        for step in pipeline.pipeline:
            if not step.enabled:
                continue

            action_class = ACTION_REGISTRY.get(step.job)
            if action_class is None:
                raise ValueError(f"Unknown job type: '{step.job}'. Check ACTION_REGISTRY.")
            action = action_class()

            if step.params_list:
                key = step.params_list.replace("{{ ", "").replace(" }}", "")
                items = inputs.get(key, [])

                log.info("PipelineExecutor", f"Resolved dynamic params list for key='{key}', items_count={len(items)}")
                if self.cfg.debug:
                    log.debug("PipelineExecutor", f"Dynamic params raw value for key='{key}': {items}")
                if self.cfg.debug:
                    log.debug("PipelineExecutor",
                              f"Entering dynamic iteration loop for step '{step.name}' with total={len(items)}")

                if not isinstance(items, list):
                    log.error("PipelineExecutor",
                              f"Invalid params list for key='{key}'. Expected list, got: {type(items)}")
                    raise ValueError(f"Invalid params list for key='{key}'")

                for index, params in enumerate(items):
                    try:
                        if self.cfg.debug:
                            log.debug("PipelineExecutor",
                                      f"[{step.name}] Executing dynamic iteration {index + 1}/{len(items)} with params={params}")
                        if self.cfg.debug:
                            log.debug(
                                "PipelineExecutor",
                                f"[{step.name}] Iteration {index + 1}/{len(items)} validation start | type={type(params)}, value={params}"
                            )

                        if not isinstance(params, dict):
                            log.error(
                                "PipelineExecutor",
                                f"Iteration {index + 1}: expected dict but received {type(params)} – value={params}"
                            )
                            raise ValueError(f"Invalid params in dynamic list for step '{step.name}'")

                        if self.cfg.debug:
                            log.debug(
                                "PipelineExecutor",
                                f"[{step.name}] Iteration {index + 1}: validation passed"
                            )

                        self._run_action(step, action, params)

                    except Exception as ex:
                        if self.cfg.debug:
                            log.debug("PipelineExecutor",
                                      f"[{step.name}] Iteration {index + 1}: exception occurred → {ex}")
                        log.error("PipelineExecutor",
                                  f"Exception while executing step '{step.name}' with dynamic params: {ex}")
                        raise

                continue

            if self.cfg.debug:
                log.debug("PipelineExecutor", f"Executing step {step.name} with params: {step.params or {} }")
            self._run_action(step, action, step.params or {})

    def _run_action(self, step, action, params):
        cfg = self.cfg
        if cfg.debug:
            log.debug("PipelineExecutor", f"_run_action invoked for {step.name}")
            log.debug("PipelineExecutor", f"_run_action parameters for step '{step.name}': {params}")
        log.info("PipelineExecutor", f"Running step: {step.name} ({step.job})")
        response = action.execute(params)

        log.info("PipelineExecutor",
                 f"Result(success={response.success}, message={response.message}, data={response.data})")

        if not response.success:
            log.error("PipelineExecutor", "Pipeline failed.")
            raise RuntimeError("Pipeline execution aborted due to failed step.")
