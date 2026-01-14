from typing import Optional

from pydantic import BaseModel


class Organization(BaseModel):
    name: str
    email: Optional[str] = None
    model_config = {"extra": "ignore"}


class GetOrganization(BaseModel):
    name: str
    model_config = {"extra": "ignore"}


class DeleteOrganization(BaseModel):
    name: str
    model_config = {"extra": "ignore"}


class ListOrganizations(BaseModel):
    pass
    model_config = {"extra": "ignore"}
