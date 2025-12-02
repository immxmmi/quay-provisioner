from engine_reader.pipeline_reader import PipelineReader
from engine.action_registry import ACTION_REGISTRY


class PipelineEngine:

    def __init__(self):
        self.reader = PipelineReader()

    def load_pipeline(self, pipeline_file: str):
        pipeline = self.reader.load_pipeline(pipeline_file)
        inputs = self.reader.load_inputs(pipeline.input_file)
        pipeline = self.reader.resolve_templates(pipeline, inputs)
        self.validate_jobs(pipeline)
        return pipeline

    def validate_jobs(self, pipeline):
        for step in pipeline.pipeline:
            job = step.job

            if job not in ACTION_REGISTRY:
                raise ValueError(
                    f"\nPipeline Error:\n"
                    f"   Step: '{step.name}'\n"
                    f"   Invalid job: '{job}'\n\n"
                    f"💡 Reason:\n"
                    f"   This job is not registered in the ActionRegistry.\n\n"
                    f"   Allowed jobs:\n"
                    f"   {', '.join(ACTION_REGISTRY.keys())}\n\n"
                    f"   Fix:\n"
                    f"   - Correct the job name in pipeline.yaml\n"
                    f"   - Or add an Action for this job in the ActionRegistry.\n"
                )

    def debug_print(self, pipeline):
        print("📌 Loaded Pipeline:")
        for step in pipeline.pipeline:
            print(f"Step: {step.name}")
            print(f"  job: {step.job}")
            print(f"  enabled: {step.enabled}")
            print(f"  params: {step.params}")
            print()

    def run_pipeline(self, pipeline):
        for step in pipeline.pipeline:
            if not step.enabled:
                continue

            action_class = ACTION_REGISTRY.get(step.job)
            action = action_class()

            # Run multiple executions via params_list
            if hasattr(step, "params_list") and step.params_list:
                list_expr = step.params_list.strip()
                inputs = self.reader.load_inputs(pipeline.input_file)

                if list_expr.startswith("{{ inputs.") and list_expr.endswith(" }}"):
                    key = list_expr[len("{{ inputs."): -len(" }}")].strip()
                    items = inputs.get(key, [])
                else:
                    items = []

                for params in items:
                    print(f"▶ Running step: {step.name} ({step.job})")
                    response = action.execute(params or {})
                    print(f"   ✔ Success: {response.success}")
                    if response.message:
                        print(f"   ✔ Message: {response.message}")
                    if response.data:
                        print(f"   ✔ Data: {response.data}")
                    print()
                    if not response.success:
                        print("❌ Pipeline failed.")
                        import sys
                        sys.exit(1)

                continue

            print(f"▶ Running step: {step.name} ({step.job})")

            response = action.execute(step.params or {})

            print(f"   ✔ Success: {response.success}")
            if response.message:
                print(f"   ✔ Message: {response.message}")
            if response.data:
                print(f"   ✔ Data: {response.data}")
            print()
            if not response.success:
                print("❌ Pipeline failed.")
                import sys
                sys.exit(1)