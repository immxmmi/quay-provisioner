from actions.base_action import BaseAction
from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.organization_model import GetOrganization
from utils.logger import Logger as log


class GetOrganizationAction(BaseAction):

    @staticmethod
    def exists(name: str) -> bool:
        """Check if an organization exists."""
        try:
            gateway = QuayGateway()
            result = gateway.get_organization(name)
            return result is not None
        except Exception as e:
            log.debug("GetOrganizationAction", f"Error checking if organization exists: {e}")
            if "404" in str(e):
                return False
            raise

    def execute(self, data: dict) -> ActionResponse:
        try:
            log.info("GetOrganizationAction", f"Executing organization lookup payload={data}")
            org = GetOrganization(**data)
            log.debug("GetOrganizationAction", f"Validated input model={org.model_dump()}")

            result = self.gateway.get_organization(org.name)
            log.info("GetOrganizationAction", f"Organization fetch succeeded name={org.name}")

            return ActionResponse(
                success=True,
                message="Organization fetched successfully",
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            log.error("GetOrganizationAction", f"Organization fetch failed: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to get organization: {e}"
            )
