from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.robot_account_model import GetRobotAccount
from utils.logger import Logger as log


class GetRobotAccountAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    @staticmethod
    def exists(organization: str, robot: str) -> bool:
        try:
            gateway = QuayGateway()
            result = gateway.get_robot_account(
                organization=organization,
                robot_shortname=robot
            )
            return result is not None
        except Exception as e:
            msg = str(e)
            # Quay returns 400 for non-existing robots
            if "400" in msg and "Could not find robot" in msg:
                return False
            # 404 fallback
            if "404" in msg:
                return False
            raise e

    def execute(self, data: dict):
        try:
            log.info("GetRobotAccountAction", f"Executing with data: {data}")

            dto = GetRobotAccount(**data)
            log.debug("GetRobotAccountAction", f"Filtered model data: {dto.model_dump()}")

            org = data.get("organization")
            if not org:
                raise ValueError("Missing required field: 'organization'")

            result = self.gateway.get_robot_account(
                organization=org,
                robot_shortname=dto.robot_shortname
            )

            log.info("GetRobotAccountAction", f"API result: {result}")

            return ActionResponse(
                success=True,
                data={
                    "organization": org,
                    "robot": dto.robot_shortname,
                    "result": result
                }
            )

        except Exception as e:
            log.error("GetRobotAccountAction", f"ERROR: {e}")
            return ActionResponse(success=False, message=str(e))