from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.robot_account_model import GetRobotAccount


class GetRobotAccountAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    def execute(self, data: dict):
        try:
            print(f"[GetRobotAccountAction] Executing with data: {data}")

            dto = GetRobotAccount(**data)
            print(f"[GetRobotAccountAction] Filtered model data: {dto.model_dump()}")

            org = data.get("organization")
            if not org:
                raise ValueError("Missing required field: 'organization'")

            result = self.gateway.get_robot_account(
                organization=org,
                robot_shortname=dto.robot_shortname
            )

            print(f"[GetRobotAccountAction] API result: {result}")

            return ActionResponse(
                success=True,
                data={
                    "organization": org,
                    "robot": dto.robot_shortname,
                    "result": result
                }
            )

        except Exception as e:
            print(f"[GetRobotAccountAction] ERROR: {e}")
            return ActionResponse(success=False, message=str(e))