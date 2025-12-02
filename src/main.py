from engine.pipeline_engine import PipelineEngine
from config.loader import TARGET_FILE



engine = PipelineEngine()

pipeline = engine.load_pipeline(TARGET_FILE)
engine.debug_print(pipeline)
engine.run_pipeline(pipeline)