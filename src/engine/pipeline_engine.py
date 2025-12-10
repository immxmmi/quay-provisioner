from engine_reader.pipeline_reader import PipelineReader
from engine.pipeline_validator import PipelineValidator
from engine.pipeline_executor import PipelineExecutor
from config.loader import Config
import sys
from utils.logger import Logger as log

class PipelineEngine:

    def __init__(self, config):
        self.reader = PipelineReader()
        self.validator = PipelineValidator()
        self.executor = PipelineExecutor()
        self.config = config

    def load_pipeline(self, pipeline_file: str):
        try:
            cfg = Config()
            if cfg.debug:
                log.debug("PipelineEngine", f"Loading pipeline file: {pipeline_file}")

            pipeline = self.reader.load_pipeline(pipeline_file)
            inputs = self.reader.load_inputs(self.config.inputs_file)
            if cfg.debug:
                log.debug("PipelineEngine", f"Loaded inputs from: {self.config.inputs_file}")
                log.debug("PipelineEngine", f"Inputs content: {inputs}")

            pipeline = self.reader.resolve_templates(pipeline, inputs)
            if cfg.debug:
                log.debug("PipelineEngine", "Templates resolved")

            self.validator.validate_jobs(pipeline)
            if cfg.debug:
                log.info("PipelineEngine", "Pipeline validation completed")
            return pipeline

        except Exception as e:
            log.error("PipelineEngine", f"Pipeline validation failed: {e}")
            sys.exit(1)

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
            cfg = Config()
            if cfg.debug:
                log.info("PipelineEngine", "Starting pipeline execution")

            self.executor.run_pipeline(pipeline, self.config.inputs_file)
        except Exception as e:
            cfg = Config()
            if cfg.debug:
                log.debug("PipelineEngine", f"Execution error detail: {e}")
            log.error("PipelineEngine", f"Pipeline execution failed: {e}")
            sys.exit(1)