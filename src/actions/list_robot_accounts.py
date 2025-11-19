from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.robot_account_model import ListRobotAccounts


class ListRobotAccountsAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    def execute(self, data: dict):
        try:
            print(f"[ListRobotAccountsAction] Executing with data: {data}")
            dto = ListRobotAccounts(**data)
            print(f"[ListRobotAccountsAction] Filtered model data: {dto.model_dump()}")

            org = data.get("organization")
            if not org:
                raise ValueError("Missing required field: 'organization'")

            result = self.gateway.list_robot_accounts(org)

            print(f"[ListRobotAccountsAction] API result: {result}")

            return ActionResponse(
                success=True,
                data={"organization": org, "result": result}
            )

        except Exception as e:
            print(f"[ListRobotAccountsAction] ERROR: {e}")
            return ActionResponse(success=False, message=str(e))