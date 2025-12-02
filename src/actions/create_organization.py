from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.organization_model import Organization
from actions.get_organization import GetOrganizationAction


class CreateOrganizationAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()


    def execute(self, data: dict):
        try:
            print(f"[CreateOrganizationAction] Executing with data: {data}")
            org = Organization(**data)
            print(f"[CreateOrganizationAction] Filtered model data: {org.model_dump()}")

            # --- VALIDATION ---
            print(f"[CreateOrganizationAction] Checking if organization exists: {org.name}")
            if GetOrganizationAction.exists(org.name):
                print(f"[CreateOrganizationAction] Organization already exists: {org.name}")
                return ActionResponse(
                    success=True,
                    message="Organization already exists",
                    data={"organization": org.name}
                )

            # --- CREATE NEW ORG ---
            result = self.gateway.create_organization(org.name)
            print(f"[CreateOrganizationAction] API result: {result}")

            return ActionResponse(
                success=True,
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            print(f"[CreateOrganizationAction] ERROR: {e}")
            return ActionResponse(
                success=False,
                message=str(e)
            )