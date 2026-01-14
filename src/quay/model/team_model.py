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


class RemoveTeamMember(BaseModel):
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


class TeamSyncStatusRequest(BaseModel):
    team_name: str

    model_config = {"extra": "ignore"}


class TeamRepositoryPermission(BaseModel):
    team_name: str
    repository: str
    permission: Literal["read", "write", "admin"] = "read"

    model_config = {"extra": "ignore"}


class RemoveTeamRepositoryPermission(BaseModel):
    team_name: str
    repository: str

    model_config = {"extra": "ignore"}


class PrototypeDelegate(BaseModel):
    name: str
    kind: Literal["team", "user"]

    model_config = {"extra": "ignore"}


class DefaultRepositoryPermission(BaseModel):
    delegate: PrototypeDelegate
    role: Literal["read", "write", "admin"] = "read"
    activating_user: Optional[str] = None

    model_config = {"extra": "ignore"}


class RemoveDefaultRepositoryPermission(BaseModel):
    delegate: PrototypeDelegate
    role: Optional[Literal["read", "write", "admin"]] = None

    model_config = {"extra": "ignore"}


class InviteTeamMember(BaseModel):
    team_name: str
    email: str

    model_config = {"extra": "ignore"}


class DeleteTeamInvite(BaseModel):
    team_name: str
    email: str

    model_config = {"extra": "ignore"}
