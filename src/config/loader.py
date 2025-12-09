import os
from pathlib import Path

import yaml

class Config:
    def __init__(self):
        config_file = Path(__file__).parent / "settings.yaml"
        pipelines_dir = Path(__file__).parent.parent / "pipelines"
        pipelines_dir.mkdir(parents=True, exist_ok=True)

        BASE_DIR = Path(__file__).resolve().parent.parent

        pipeline_env = os.getenv("PIPELINE_FILE")
        if pipeline_env:
            self.pipeline_file = Path(pipeline_env).resolve()
        else:
            self.pipeline_file = (BASE_DIR / "pipelines" / "pipeline.yaml").resolve()

        self.inputs_file = (BASE_DIR / "pipelines" / "inputs.yaml").resolve()

        data = yaml.safe_load(config_file.read_text())

        env_base = os.getenv("QUAY_API_BASE_URL")
        env_token = os.getenv("QUAY_API_TOKEN")

        self.base_url = env_base if env_base and env_base.strip() else data["api"].get("base_url")
        self.token = env_token if env_token and env_token.strip() else data["api"].get("token")

        if not self.base_url:
            raise ValueError("QUAY_API_BASE_URL is not set in environment variables or settings.yaml")

        if not self.token:
            raise ValueError("QUAY_API_TOKEN is not set in environment variables or settings.yaml")
