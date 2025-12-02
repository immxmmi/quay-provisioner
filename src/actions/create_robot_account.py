from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.robot_account_model import CreateRobotAccount
from actions.get_robot_account import GetRobotAccountAction
from actions.get_organization import GetOrganizationAction


class CreateRobotAccountAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    def execute(self, data: dict):
        try:
            print(f"[CreateRobotAccountAction] Executing with data: {data}")
            dto = CreateRobotAccount(**data)
            print(f"[CreateRobotAccountAction] Filtered model data: {dto.model_dump()}")

            org = data.get("organization")
            if not org:
                raise ValueError("Missing required field: 'organization'")

            # --- VALIDATION ---
            print(f"[CreateRobotAccountAction] Checking if organization exists: {org}")
            if not GetOrganizationAction.exists(org):
                print(f"[CreateRobotAccountAction] Organization does NOT exist: {org}")
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            print(f"[CreateRobotAccountAction] Checking if robot account exists: {org}/{dto.robot_shortname}")
            if GetRobotAccountAction.exists(org, dto.robot_shortname):
                print(f"[CreateRobotAccountAction] Robot already exists: {dto.robot_shortname}")
                return ActionResponse(
                    success=True,
                    message="Robot account already exists",
                    data={"organization": org, "robot": dto.robot_shortname}
                )

            # --- CREATE NEW ROBOT ---
            result = self.gateway.create_robot_account(
                organization=org,
                robot_shortname=dto.robot_shortname,
                description=dto.description
            )

            print(f"[CreateRobotAccountAction] API result: {result}")

            return ActionResponse(
                success=True,
                data={"organization": org, "robot": dto.robot_shortname, "result": result}
            )

        except Exception as e:
            print(f"[CreateRobotAccountAction] ERROR: {e}")
            return ActionResponse(success=False, message=str(e))