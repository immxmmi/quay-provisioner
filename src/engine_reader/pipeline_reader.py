from pathlib import Path

import yaml

from exceptions import ConfigurationError
from model.pipeline_model import PipelineDefinition
from utils.logger import Logger as log


class PipelineReader:

    def load_pipeline(self, file_path: str) -> PipelineDefinition:
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Pipeline file not found: {file_path}")

        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in pipeline file: {e}") from e

        if not data:
            raise ConfigurationError(f"Pipeline file is empty: {file_path}")

        log.debug("PipelineReader", f"load_pipeline file={file_path}")
        log.debug("PipelineReader", f"load_pipeline content={data}")
        return PipelineDefinition(**data)

    def load_inputs(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Inputs file not found: {file_path}")

        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in inputs file: {e}") from e

        log.debug("PipelineReader", f"load_inputs file={file_path}")
        log.debug("PipelineReader", f"load_inputs content={data}")
        return data or {}

    def resolve_templates(self, pipeline: PipelineDefinition, inputs: dict):
        log.debug("PipelineReader", "Starting template resolution")

        for step in pipeline.pipeline:
            if not step.params:
                continue

            log.debug("PipelineReader", f"Resolving templates for step={step.name}")

            for key, value in list(step.params.items()):
                if not isinstance(value, str):
                    continue

                if value.startswith("{{ inputs.") and value.endswith(" }}"):
                    param_key = value[len("{{ inputs."):-3].strip()

                    resolved = inputs.get(param_key)
                    log.debug(
                        "PipelineReader",
                        f"Template match: step={step.name} key={key} raw='{value}' "
                        f"resolved_key='{param_key}' resolved_value={resolved}"
                    )

                    step.params[key] = resolved
                else:
                    log.debug(
                        "PipelineReader",
                        f"No template: step={step.name} key={key} value={value}"
                    )

        log.debug("PipelineReader", "Template resolution completed")
        return pipeline
