from engine.action_registry import ACTION_REGISTRY
from engine_reader.pipeline_reader import PipelineReader
from config.loader import Config
from utils.logger import Logger as log

class PipelineExecutor:

    def __init__(self):
        self.reader = PipelineReader()

    def run_pipeline(self, pipeline, inputs_file):
        inputs = self.reader.load_inputs(inputs_file)

        cfg = Config()
        if cfg.debug:
            log.debug("PipelineExecutor", f"Executor loaded inputs: {inputs}")

        for step in pipeline.pipeline:
            if not step.enabled:
                continue

            action_class = ACTION_REGISTRY.get(step.job)
            action = action_class()

            if step.params_list:
                key = step.params_list.replace("{{ ", "").replace(" }}", "")
                items = inputs.get(key, [])

                log.info("PipelineExecutor", f"Resolved dynamic params list for key='{key}', items_count={len(items)}")

                if not isinstance(items, list):
                    log.error("PipelineExecutor", f"Invalid params list for key='{key}'. Expected list, got: {type(items)}")
                    raise ValueError(f"Invalid params list for key='{key}'")

                for index, params in enumerate(items):
                    try:
                        if cfg.debug:
                            log.debug("PipelineExecutor",
                                      f"[{step.name}] Executing dynamic iteration {index+1}/{len(items)} with params={params}")

                        if not isinstance(params, dict):
                            log.error("PipelineExecutor",
                                      f"Dynamic params entry is not a dict. Received: {params}")
                            raise ValueError(f"Invalid params in dynamic list for step '{step.name}'")

                        self._run_action(step, action, params)

                    except Exception as ex:
                        log.error("PipelineExecutor",
                                  f"Exception while executing step '{step.name}' with dynamic params: {ex}")
                        raise

                continue

            if cfg.debug:
                log.debug("PipelineExecutor", f"Executing step {step.name} with params: {step.params or {}}")
            self._run_action(step, action, step.params or {})

    def _run_action(self, step, action, params):
        cfg = Config()
        if cfg.debug:
            log.debug("PipelineExecutor", f"_run_action invoked for {step.name}")
        log.info("PipelineExecutor", f"Running step: {step.name} ({step.job})")
        response = action.execute(params)

        log.info("PipelineExecutor", f"Success: {response.success}")
        if response.message:
            log.info("PipelineExecutor", f"Message: {response.message}")
        if response.data:
            log.info("PipelineExecutor", f"Data: {response.data}")

        if not response.success:
            log.error("PipelineExecutor", "Pipeline failed.")
            import sys
            sys.exit(1)