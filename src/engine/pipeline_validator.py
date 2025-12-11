from engine.action_registry import ACTION_REGISTRY
from utils.logger import Logger as log


class PipelineValidator:

    def validate_jobs(self, pipeline):
        log.debug("PipelineValidator", "Validating jobs in pipeline")
        log.info("PipelineValidator", f"Starting job validation for {len(pipeline.pipeline)} steps")
        for step in pipeline.pipeline:
            log.debug("PipelineValidator", f"Checking job '{step.job}' for step '{step.name}'")
            if step.job not in ACTION_REGISTRY:
                allowed = ", ".join(ACTION_REGISTRY.keys())

                log.error("PipelineValidator", f"Invalid job '{step.job}' in step '{step.name}'")
                log.info("PipelineValidator", f"Allowed jobs: {allowed}")
                log.debug("PipelineValidator", f"Validation failed for step '{step.name}' with job '{step.job}'")

                raise ValueError(
                    f"Invalid job '{step.job}' in step '{step.name}'. Allowed jobs: {allowed}"
                )
        log.info("PipelineValidator", "Job validation completed successfully")
