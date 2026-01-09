from actions.base_action import BaseAction
from model.action_response import ActionResponse
from utils.logger import Logger as log


class ListOrganizationsAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            log.info("ListOrganizationsAction", f"Executing with data: {data}")
            result = self.gateway.list_organizations()
            log.debug("ListOrganizationsAction", f"API result: {result}")

            return ActionResponse(
                success=True,
                message="Organizations listed successfully",
                data={"result": result}
            )

        except Exception as e:
            log.error("ListOrganizationsAction", f"Failed to list organizations: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to list organizations: {e}"
            )
