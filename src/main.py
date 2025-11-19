from flask import Flask
from git_watcher.watcher import create_webhook_blueprint

from engine.pipeline_engine import PipelineEngine

TARGET_FILE = "pipelines/pipeline.yaml"

engine = PipelineEngine()

pipeline = engine.load_pipeline(TARGET_FILE)
engine.debug_print(pipeline)
engine.run_pipeline(pipeline)

# engine.run_pipeline(pipeline)

##app = Flask(__name__)
##app.register_blueprint(create_webhook_blueprint(TARGET_FILE))

##if __name__ == "__main__":
##    app.run(host="0.0.0.0", port=8000)