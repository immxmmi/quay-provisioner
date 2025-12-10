from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.organization_model import Organization
from actions.get_organization import GetOrganizationAction
from utils.logger import Logger as log


class CreateOrganizationAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()


    def execute(self, data: dict):
        try:
            log.info("CreateOrganizationAction", f"Executing with data: {data}")
            org = Organization(**data)
            log.debug("CreateOrganizationAction", f"Filtered model data: {org.model_dump()}")

            # --- VALIDATION ---
            log.info("CreateOrganizationAction", f"Checking if organization exists: {org.name}")
            if GetOrganizationAction.exists(org.name):
                log.info("CreateOrganizationAction", f"Organization already exists: {org.name}")
                return ActionResponse(
                    success=True,
                    message="Organization already exists",
                    data={"organization": org.name}
                )

            # --- CREATE NEW ORG ---
            result = self.gateway.create_organization(org.name)
            log.info("CreateOrganizationAction", f"API result: {result}")

            return ActionResponse(
                success=True,
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            log.error("CreateOrganizationAction", f"ERROR: {e}")
            return ActionResponse(
                success=False,
                message=str(e)
            )