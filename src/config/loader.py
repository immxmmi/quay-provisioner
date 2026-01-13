import os
from pathlib import Path
from typing import Optional

import yaml

from utils.logger import Logger as log


class Config:
    """Configuration singleton with validation and error handling."""

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        config_file = Path(__file__).parent / "settings.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            data = yaml.safe_load(config_file.read_text())
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}") from e

        if not data:
            raise ValueError("Configuration file is empty")

        app_cfg = data.get("app", {})
        self.version = os.getenv("APP_VERSION", app_cfg.get("version", "unknown"))

        debug_cfg = data.get("debug", {})
        self.debug = os.getenv("DEBUG_ENABLED", str(debug_cfg.get("enabled", "false"))).lower() == "true"
        log.configure(self.debug)

        BASE_DIR = Path(__file__).resolve().parent.parent

        self.pipeline_file = Path(os.getenv("PIPELINE_FILE", BASE_DIR / "pipelines/pipeline.yaml")).resolve()
        self.inputs_file = Path(os.getenv("INPUTS_FILE", BASE_DIR / "pipelines/inputs.yaml")).resolve()

        api = data["api"]
        auth = data.get("auth", {})

        # --- API CONFIG ---
        raw_host = os.getenv("API_HOST", api.get("host"))
        if not raw_host:
            raise ValueError("API_HOST must be set via settings.yaml or environment variable")

        if raw_host.startswith("http://") or raw_host.startswith("https://"):
            self.host = raw_host.rstrip("/")
        else:
            self.host = f"http://{raw_host}".rstrip("/")

        try:
            self.port = int(os.getenv("API_PORT", api.get("port", 443)))
        except (ValueError, TypeError) as e:
            raise ValueError(f"API_PORT must be a valid integer: {e}") from e

        if not 1 <= self.port <= 65535:
            raise ValueError(f"API_PORT must be between 1 and 65535, got: {self.port}")

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

        if not self.token:
            raise ValueError("API_TOKEN must be set via settings.yaml or environment variable")

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
