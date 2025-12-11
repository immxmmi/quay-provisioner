import yaml
from pathlib import Path
from model.pipeline_model import PipelineDefinition
from utils.logger import Logger as log


class PipelineReader:
    def load_pipeline(self, file_path: str) -> PipelineDefinition:
        data = yaml.safe_load(Path(file_path).read_text())
        log.debug("PipelineReader", f"load_pipeline file={file_path}")
        log.debug("PipelineReader", f"load_pipeline content={data}")
        return PipelineDefinition(**data)

    def load_inputs(self, file_path: str) -> dict:
        data = yaml.safe_load(Path(file_path).read_text())
        log.debug("PipelineReader", f"load_inputs file={file_path}")
        log.debug("PipelineReader", f"load_inputs content={data}")
        return data

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