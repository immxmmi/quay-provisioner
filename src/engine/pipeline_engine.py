from engine.pipeline_executor import PipelineExecutor
from engine.pipeline_validator import PipelineValidator
from engine_reader.pipeline_reader import PipelineReader
from exceptions import PipelineError
from utils.logger import Logger as log


class PipelineEngine:

    def __init__(self, config):
        self.reader = PipelineReader()
        self.validator = PipelineValidator()
        self.executor = PipelineExecutor()
        self.config = config

    def load_pipeline(self, pipeline_file: str):
        try:
            log.debug("PipelineEngine", f"Loading pipeline file: {pipeline_file}")

            pipeline = self.reader.load_pipeline(pipeline_file)
            log.debug("PipelineEngine", f"Raw pipeline structure: {pipeline}")

            inputs = self.reader.load_inputs(self.config.inputs_file)
            log.debug("PipelineEngine", f"Loaded inputs from: {self.config.inputs_file}")
            log.debug("PipelineEngine", f"Inputs resolved: {inputs}")

            pipeline = self.reader.resolve_templates(pipeline, inputs)
            log.debug("PipelineEngine", f"Pipeline after template resolution: {pipeline}")
            log.debug("PipelineEngine", "Template resolution completed")

            self.validator.validate_jobs(pipeline)
            log.info("PipelineEngine", "Pipeline validation completed")
            return pipeline

        except Exception as e:
            log.error("PipelineEngine", f"Pipeline validation failed: {e}")
            raise PipelineError(f"Pipeline load/validation failed: {e}") from e

    def debug_print(self, pipeline):
        print("📌 Loaded Pipeline:")
        for step in pipeline.pipeline:
            print(f"Step: {step.name}")
            print(f"  job: {step.job}")
            print(f"  enabled: {step.enabled}")
            print(f"  params: {step.params}")
            print(f"  params_list: {step.params_list}")
            print()

    def run(self, pipeline):
        try:
            log.info("PipelineEngine", "Pipeline execution started")
            log.debug("PipelineEngine", f"Executing pipeline with input file: {self.config.inputs_file}")

            self.executor.run_pipeline(pipeline, self.config.inputs_file)
        except Exception as e:
            log.debug("PipelineEngine", f"Execution error: {e}")
            log.error("PipelineEngine", f"Pipeline execution failed: {e}")
            raise PipelineError(f"Execution failed: {e}") from e
