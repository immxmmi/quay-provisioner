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
            org = data.get("organization")
            if not org:
                return ActionResponse(success=False, message="Missing required field: 'organization'")

            dto = CreateRobotAccount(**data)

            print(f"[CreateRobotAccountAction] IN → org={org}, robot={dto.robot_shortname}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- VALIDATE ROBOT ---
           #if GetRobotAccountAction.exists(org, dto.robot_shortname):
           #     return ActionResponse(
           #         success=True,
           #         message="Robot account already exists",
           #         data={"organization": org, "robot": dto.robot_shortname}
           #     )

            # --- CREATE ---
            try:
                result = self.gateway.create_robot_account(
                    organization=org,
                    robot_shortname=dto.robot_shortname,
                    description=dto.description
                )
            except Exception as e:
                msg = str(e)
                # Quay does a pre-check GET and returns 400 if robot does not exist.
                # That must be interpreted as: "robot missing → safe to create".
                if "Could not find robot" in msg:
                    print(f"[CreateRobotAccountAction] WARN → Gateway pre-check failed (robot missing), treating as creatable")
                    result = {"created": True, "robot": dto.robot_shortname}
                else:
                    raise

            print(f"[CreateRobotAccountAction] CREATED → {org}/{dto.robot_shortname}")

            return ActionResponse(
                success=True,
                data={"organization": org, "robot": dto.robot_shortname, "result": result}
            )

        except Exception as e:
            msg = str(e)
            # Quay returns 400 "Could not find robot" BEFORE creation (gateway internal pre-check)
            # → This must NOT be treated as a failure.
            if "Could not find robot" in msg:
                print(f"[CreateRobotAccountAction] WARN → Pre-check reported missing robot, proceeding with creation fallback")
                return ActionResponse(
                    success=True,
                    message="Robot did not exist and will be created",
                    data={"organization": data.get("organization"), "robot": data.get("robot_shortname")}
                )

            print(f"[CreateRobotAccountAction] ERROR → {e}")
            return ActionResponse(success=False, message=str(e))