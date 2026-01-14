from pydantic import BaseModel


class CreateRobotAccount(BaseModel):
    robot_shortname: str
    description: str | None = None

    model_config = {"extra": "ignore"}


class RobotAccountResponse(BaseModel):
    name: str
    token: str | None = None
    created: bool | None = None

    model_config = {"extra": "ignore"}


class DeleteRobotAccount(BaseModel):
    robot_shortname: str

    model_config = {"extra": "ignore"}


class GetRobotAccount(BaseModel):
    robot_shortname: str

    model_config = {"extra": "ignore"}


class DeleteRobotResponse(BaseModel):
    success: bool
    message: str | None = None

    model_config = {"extra": "ignore"}


class ListRobotAccounts(BaseModel):
    model_config = {"extra": "ignore"}


class RobotAccountEntry(BaseModel):
    name: str

    model_config = {"extra": "ignore"}


class ListRobotResponse(BaseModel):
    robots: list[RobotAccountEntry]

    model_config = {"extra": "ignore"}
