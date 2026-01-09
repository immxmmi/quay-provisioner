from actions.base_action import BaseAction
from actions.get_organization import GetOrganizationAction
from exceptions import RobotAlreadyExistsError, ValidationError
from model.action_response import ActionResponse
from model.robot_account_model import CreateRobotAccount
from utils.logger import Logger as log


class CreateRobotAccountAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = CreateRobotAccount(**data)
            log.info("CreateRobotAccountAction", f"IN -> org={org}, robot={dto.robot_shortname}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- CREATE ---
            try:
                result = self.gateway.create_robot_account(
                    organization=org,
                    robot_shortname=dto.robot_shortname,
                    description=dto.description
                )
                log.info("CreateRobotAccountAction", f"CREATED -> {org}/{dto.robot_shortname}")

                return ActionResponse(
                    success=True,
                    data={"organization": org, "robot": dto.robot_shortname, "result": result}
                )

            except RobotAlreadyExistsError:
                log.info("CreateRobotAccountAction", f"Robot already exists: {dto.robot_shortname}")
                return ActionResponse(
                    success=True,
                    message="Robot already exists",
                    data={"organization": org, "robot": dto.robot_shortname}
                )

        except ValidationError as e:
            log.error("CreateRobotAccountAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("CreateRobotAccountAction", f"Failed to create robot account: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to create robot account: {e}"
            )
