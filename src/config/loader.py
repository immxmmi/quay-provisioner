import os
from pathlib import Path
import yaml
from utils.logger import Logger as log


class Config:

    def __init__(self):
        config_file = Path(__file__).parent / "settings.yaml"
        data = yaml.safe_load(config_file.read_text())

        app_cfg = data.get("app", {})
        self.version = os.getenv("APP_VERSION", app_cfg.get("version", "unknown"))

        debug_cfg = data.get("debug", {})
        self.debug = os.getenv("DEBUG_ENABLED", str(debug_cfg.get("enabled", "false"))).lower() == "true"
        log.configure(self.debug)

        BASE_DIR = Path(__file__).resolve().parent.parent

        self.pipeline_file = Path(os.getenv("PIPELINE_FILE", BASE_DIR / "pipelines/pipeline.yaml")).resolve()
        self.inputs_file = (BASE_DIR / "pipelines" / "inputs.yaml").resolve()

        api = data["api"]
        auth = data.get("auth", {})

        # --- API CONFIG ---
        raw_host = os.getenv("API_HOST", api.get("host"))
        if raw_host.startswith("http://") or raw_host.startswith("https://"):
            self.host = raw_host.rstrip("/")
        else:
            self.host = f"http://{raw_host}".rstrip("/")

        self.port = int(os.getenv("API_PORT", api.get("port")))

        raw_base_path = os.getenv("API_BASE_PATH", api.get("base_path", "/api/v1"))
        self.base_path = raw_base_path.rstrip("/")

        self.base_url = f"{self.host}:{self.port}{self.base_path}"

        if self.debug:
            log.debug("Config", f"Config raw_host={raw_host}")
            log.debug("Config", f"Config normalized_host={self.host}")
            log.debug("Config", f"Config port={self.port}")
            log.debug("Config", f"Config raw_base_path={raw_base_path}")
            log.debug("Config", f"Config normalized_base_path={self.base_path}")
            log.debug("Config", f"Config base_url={self.base_url}")
            log.debug("Config", f"App version={self.version}")

        # --- AUTH CONFIG ---
        self.auth_type = os.getenv("API_AUTH_TYPE", auth.get("type", "bearer"))
        self.token = os.getenv("API_TOKEN", auth.get("token"))

        if not raw_host:
            raise ValueError("API_HOST must be set via settings.yaml or environment variable")

        if not self.token:
            raise ValueError("API_TOKEN must be set via settings.yaml or environment variable")