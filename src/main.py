from engine.pipeline_engine import PipelineEngine
from config.loader import Config
from datetime import datetime

config = Config()

start_ts = datetime.now()
print(f"[INFO] Pipeline execution started at {start_ts.isoformat()}")

if config.debug:
    print("[DEBUG]: Loaded configuration:", config.__dict__)

engine = PipelineEngine(config)

pipeline = engine.load_pipeline(config.pipeline_file)

if config.debug:
    engine.debug_print(pipeline)

engine.run(pipeline)

end_ts = datetime.now()
duration = (end_ts - start_ts).total_seconds()

print(f"[INFO] Pipeline execution finished at {end_ts.isoformat()} ({duration}s)")