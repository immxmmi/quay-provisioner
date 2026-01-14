from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from exceptions import TeamNotFoundError, ValidationError
from quay.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from quay.model.team_model import GetTeam
from utils.logger import Logger as log


class GetTeamAction(BaseAction):

    @staticmethod
    def exists(organization: str, team_name: str) -> bool:
        """Check if a team exists in the organization."""
        try:
            gw = QuayGateway()
            gw.get_team(organization, team_name)
            return True
        except TeamNotFoundError:
            return False
        except Exception:
            return False

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = GetTeam(**data)
            log.info("GetTeamAction", f"IN -> org={org}, team={dto.team_name}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- GET ---
            try:
                result = self.gateway.get_team(org, dto.team_name)
                log.info("GetTeamAction", f"FOUND -> {org}/{dto.team_name}")

                return ActionResponse(
                    success=True,
                    data={"organization": org, "team": dto.team_name, "members": result}
                )

            except TeamNotFoundError:
                log.info("GetTeamAction", f"Team not found: {dto.team_name}")
                return ActionResponse(
                    success=False,
                    message="Team not found",
                    data={"organization": org, "team": dto.team_name}
                )

        except ValidationError as e:
            log.error("GetTeamAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("GetTeamAction", f"Failed to get team: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to get team: {e}"
            )
