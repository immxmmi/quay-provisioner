from engine.pipeline_engine import PipelineEngine

TARGET_FILE = "pipelines/pipeline.yaml"

engine = PipelineEngine()

pipeline = engine.load_pipeline(TARGET_FILE)
engine.debug_print(pipeline)
engine.run_pipeline(pipeline)