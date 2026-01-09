from datetime import datetime

from config.loader import Config
from engine.pipeline_engine import PipelineEngine
from utils.logger import Logger as log

config = Config()

start_ts = datetime.now()
log.info("Main", f"Pipeline execution started at {start_ts.isoformat()}")

log.debug("Main", f"Loaded configuration: {config.__dict__}")

engine = PipelineEngine(config)

pipeline = engine.load_pipeline(config.pipeline_file)

if config.debug:
    engine.debug_print(pipeline)

engine.run(pipeline)

end_ts = datetime.now()
duration = (end_ts - start_ts).total_seconds()

log.info("Main", f"Pipeline execution finished at {end_ts.isoformat()} ({duration}s)")
