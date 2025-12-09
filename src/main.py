from engine.pipeline_engine import PipelineEngine
from config.loader import Config

config = Config()
engine = PipelineEngine(config)

pipeline = engine.load_pipeline(config.pipeline_file)
engine.debug_print(pipeline)
engine.run_pipeline(pipeline)