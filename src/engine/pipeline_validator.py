from engine.action_registry import ACTION_REGISTRY

class PipelineValidator:

    def validate_jobs(self, pipeline):
        for step in pipeline.pipeline:
            if step.job not in ACTION_REGISTRY:
                allowed = ", ".join(ACTION_REGISTRY.keys())
                raise ValueError(
                    f"Invalid job '{step.job}' in step '{step.name}'. "
                    f"Allowed jobs: {allowed}"
                )