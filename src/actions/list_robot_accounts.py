from actions.base_action import BaseAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from model.robot_account_model import ListRobotAccounts
from utils.logger import Logger as log


class ListRobotAccountsAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            log.info("ListRobotAccountsAction", f"Executing with data: {data}")
            dto = ListRobotAccounts(**data)
            log.debug("ListRobotAccountsAction", f"Filtered model data: {dto.model_dump()}")

            result = self.gateway.list_robot_accounts(org)

            log.info("ListRobotAccountsAction", f"Listed robots for org: {org}")

            return ActionResponse(
                success=True,
                data={"organization": org, "result": result}
            )

        except ValidationError as e:
            log.error("ListRobotAccountsAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("ListRobotAccountsAction", f"Failed to list robot accounts: {e}")
            return ActionResponse(success=False, message=f"Failed to list robot accounts: {e}")
