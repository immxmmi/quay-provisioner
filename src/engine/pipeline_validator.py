import sys
from engine.action_registry import ACTION_REGISTRY
from config.loader import Config
from utils.logger import Logger as log

class PipelineValidator:

    def validate_jobs(self, pipeline):
        cfg = Config()
        if cfg.debug:
            log.debug("PipelineValidator", "Validating jobs in pipeline")
        for step in pipeline.pipeline:
            if cfg.debug:
                log.debug("PipelineValidator", f"Checking job '{step.job}' for step '{step.name}'")
            if step.job not in ACTION_REGISTRY:
                allowed = ", ".join(ACTION_REGISTRY.keys())

                log.error("PipelineValidator", f"Invalid job '{step.job}' in step '{step.name}'")
                log.info("PipelineValidator", f"Allowed jobs: {allowed}")
                if cfg.debug:
                    log.debug("PipelineValidator", f"Validation failed for step '{step.name}' with job '{step.job}'")

                sys.exit(1)