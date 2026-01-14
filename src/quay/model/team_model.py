from typing import Literal, Optional

from pydantic import BaseModel


class CreateTeam(BaseModel):
    team_name: str
    role: Literal["member", "creator", "admin"] = "member"
    description: Optional[str] = None

    model_config = {"extra": "ignore"}


class GetTeam(BaseModel):
    team_name: str

    model_config = {"extra": "ignore"}


class DeleteTeam(BaseModel):
    team_name: str

    model_config = {"extra": "ignore"}


class AddTeamMember(BaseModel):
    team_name: str
    member_name: str

    model_config = {"extra": "ignore"}


class TeamResponse(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None

    model_config = {"extra": "ignore"}


class SyncTeamLdap(BaseModel):
    team_name: str
    group_dn: str

    model_config = {"extra": "ignore"}


class UnsyncTeamLdap(BaseModel):
    team_name: str

    model_config = {"extra": "ignore"}
