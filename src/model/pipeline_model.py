from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PipelineStep(BaseModel):
    name: str
    job: str
    enabled: bool = True
    params: Optional[Dict[str, Any]] = None
    params_list: Optional[Any] = None


class PipelineDefinition(BaseModel):
    pipeline: List[PipelineStep]
