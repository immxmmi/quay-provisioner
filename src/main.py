import sys
from datetime import datetime

from config.loader import Config
from engine.pipeline_engine import PipelineEngine
from utils.display import Display
from utils.logger import Logger as log


def main():
    config = Config()

    # Show banner
    Display.banner(config.version, config.debug)

    start_ts = datetime.now()
    log.debug("Main", f"Loaded configuration: {config.__dict__}")

    engine = PipelineEngine(config)

    try:
        pipeline = engine.load_pipeline(config.pipeline_file)

        # Show pipeline overview (always, with more details in debug mode)
        engine.show_overview(pipeline, debug=config.debug)

        # Show execution header
        enabled_steps = len([s for s in pipeline.pipeline if s.enabled])
        Display.pipeline_start(str(config.pipeline_file), enabled_steps)

        engine.run(pipeline)

    except Exception as e:
        log.error("Main", f"Pipeline failed: {e}")
        end_ts = datetime.now()
        duration = (end_ts - start_ts).total_seconds()
        Display.summary(engine.executor.stats, duration)
        sys.exit(1)

    end_ts = datetime.now()
    duration = (end_ts - start_ts).total_seconds()

    # Show summary
    Display.summary(engine.executor.stats, duration)

    if engine.executor.stats.failed_steps > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
