from actions.base_action import BaseAction
from actions.get_organization import GetOrganizationAction
from actions.get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from model.team_model import DeleteTeam
from utils.logger import Logger as log


class DeleteTeamAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = DeleteTeam(**data)
            log.info("DeleteTeamAction", f"IN -> org={org}, team={dto.team_name}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- CHECK IF TEAM EXISTS ---
            if not GetTeamAction.exists(org, dto.team_name):
                log.info("DeleteTeamAction", f"Team does not exist: {dto.team_name}")
                return ActionResponse(
                    success=True,
                    message="Team does not exist",
                    data={"organization": org, "team": dto.team_name}
                )

            # --- DELETE ---
            result = self.gateway.delete_team(org, dto.team_name)
            log.info("DeleteTeamAction", f"DELETED -> {org}/{dto.team_name}")

            return ActionResponse(
                success=True,
                data={"organization": org, "team": dto.team_name, "result": result}
            )

        except ValidationError as e:
            log.error("DeleteTeamAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("DeleteTeamAction", f"Failed to delete team: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to delete team: {e}"
            )
