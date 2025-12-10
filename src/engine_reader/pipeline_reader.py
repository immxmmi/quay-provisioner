import yaml
from pathlib import Path
from model.pipeline_model import PipelineDefinition
from utils.logger import Logger as log


class PipelineReader:
    def load_pipeline(self, file_path: str) -> PipelineDefinition:
        data = yaml.safe_load(Path(file_path).read_text())
        from config.loader import Config
        cfg = Config()
        if cfg.debug:
            log.debug("PipelineReader", f"load_pipeline file={file_path}")
            log.debug("PipelineReader", f"load_pipeline content={data}")
        return PipelineDefinition(**data)

    def load_inputs(self, file_path: str) -> dict:
        from config.loader import Config
        cfg = Config()
        data = yaml.safe_load(Path(file_path).read_text())
        if cfg.debug:
            log.debug("PipelineReader", f"load_inputs file={file_path}")
            log.debug("PipelineReader", f"load_inputs content={data}")
        return data

    def resolve_templates(self, pipeline: PipelineDefinition, inputs: dict):
        for step in pipeline.pipeline:
            if step.params:
                for key, value in step.params.items():
                    if isinstance(value, str) and value.startswith("{{ inputs."):
                        param_key = value.replace("{{ inputs.", "").replace(" }}", "")
                        from config.loader import Config
                        cfg = Config()
                        if cfg.debug:
                            log.debug("PipelineReader", f"resolve_templates step={step.name} key={key} old={value} new={inputs.get(param_key)}")
                        step.params[key] = inputs.get(param_key)
        return pipeline