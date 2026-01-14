from ..base_action import BaseAction
from .get_organization import GetOrganizationAction
from model.action_response import ActionResponse
from quay.model.organization_model import Organization
from utils.logger import Logger as log


class CreateOrganizationAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            log.info("CreateOrganizationAction", "Starting organization creation flow")
            org = Organization(**data)
            log.debug("CreateOrganizationAction", f"Resolved model: {org.model_dump()}")

            # --- VALIDATION ---
            log.info("CreateOrganizationAction", f"Validating existence: {org.name}")
            if GetOrganizationAction.exists(org.name):
                log.info("CreateOrganizationAction", f"Organization already exists: {org.name}")
                return ActionResponse(success=True, data={"organization": org.name})

            # --- CREATE NEW ORG ---
            result = self.gateway.create_organization(org.name, email=org.email)
            log.info("CreateOrganizationAction", "Organization created successfully")

            return ActionResponse(
                success=True,
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            log.error("CreateOrganizationAction", f"Exception occurred: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to create organization: {e}"
            )
