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

                for params in items:
                    if cfg.debug:
                        log.debug("PipelineExecutor", f"Executing step {step.name} with params: {params}")
                    self._run_action(step, action, params)
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