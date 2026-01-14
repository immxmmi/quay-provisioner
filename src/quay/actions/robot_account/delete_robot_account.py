from ..base_action import BaseAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.robot_account_model import DeleteRobotAccount
from utils.logger import Logger as log


class DeleteRobotAccountAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            log.info("DeleteRobotAccountAction", f"Executing with data: {data}")
            dto = DeleteRobotAccount(**data)
            log.debug("DeleteRobotAccountAction", f"Filtered model data: {dto.model_dump()}")

            result = self.gateway.delete_robot_account(
                organization=org,
                robot_shortname=dto.robot_shortname
            )

            log.info("DeleteRobotAccountAction", f"Deleted robot: {org}/{dto.robot_shortname}")

            return ActionResponse(
                success=True,
                data={"organization": org, "robot": dto.robot_shortname, "result": result}
            )

        except ValidationError as e:
            log.error("DeleteRobotAccountAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("DeleteRobotAccountAction", f"Failed to delete robot account: {e}")
            return ActionResponse(success=False, message=f"Failed to delete robot account: {e}")
