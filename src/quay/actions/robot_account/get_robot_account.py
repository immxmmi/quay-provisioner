from ..base_action import BaseAction
from exceptions import RobotNotFoundError, ValidationError
from quay.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from quay.model.robot_account_model import GetRobotAccount
from utils.logger import Logger as log


class GetRobotAccountAction(BaseAction):

    @staticmethod
    def exists(organization: str, robot: str) -> bool:
        """Check if a robot account exists."""
        try:
            gateway = QuayGateway()
            gateway.get_robot_account(
                organization=organization,
                robot_shortname=robot
            )
            return True
        except RobotNotFoundError:
            return False
        except Exception as e:
            log.debug("GetRobotAccountAction", f"Error checking if robot exists: {e}")
            if "404" in str(e) or "400" in str(e):
                return False
            raise

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            log.info("GetRobotAccountAction", f"Executing with data: {data}")
            dto = GetRobotAccount(**data)
            log.debug("GetRobotAccountAction", f"Filtered model data: {dto.model_dump()}")

            result = self.gateway.get_robot_account(
                organization=org,
                robot_shortname=dto.robot_shortname
            )

            log.info("GetRobotAccountAction", f"Robot fetch succeeded: {org}/{dto.robot_shortname}")

            return ActionResponse(
                success=True,
                data={
                    "organization": org,
                    "robot": dto.robot_shortname,
                    "result": result
                }
            )

        except RobotNotFoundError as e:
            log.info("GetRobotAccountAction", f"Robot not found: {e}")
            return ActionResponse(
                success=False,
                message="Robot account not found"
            )

        except ValidationError as e:
            log.error("GetRobotAccountAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("GetRobotAccountAction", f"Failed to get robot account: {e}")
            return ActionResponse(success=False, message=f"Failed to get robot account: {e}")
