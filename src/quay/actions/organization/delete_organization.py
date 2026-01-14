from ..base_action import BaseAction
from model.action_response import ActionResponse
from quay.model.organization_model import DeleteOrganization
from utils.logger import Logger as log


class DeleteOrganizationAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            log.info("DeleteOrganizationAction", f"Executing with data: {data}")
            org = DeleteOrganization(**data)
            log.debug("DeleteOrganizationAction", f"Filtered model data: {org.model_dump()}")

            result = self.gateway.delete_organization(org.name)

            return ActionResponse(
                success=True,
                message="Organization deleted successfully",
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            log.error("DeleteOrganizationAction", f"Failed to delete organization: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to delete organization: {e}"
            )
