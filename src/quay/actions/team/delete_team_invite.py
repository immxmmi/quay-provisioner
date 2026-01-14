from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import DeleteTeamInvite
from utils.logger import Logger as log


class DeleteTeamInviteAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = DeleteTeamInvite(**data)
            log.info(
                "DeleteTeamInviteAction",
                f"IN -> org={org}, team={dto.team_name}, email={dto.email}"
            )

            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            if not GetTeamAction.exists(org, dto.team_name):
                return ActionResponse(
                    success=False,
                    message="Team does not exist",
                    data={"organization": org, "team": dto.team_name}
                )

            try:
                result = self.gateway.delete_team_invite(
                    organization=org,
                    team_name=dto.team_name,
                    email=dto.email
                )
                log.info(
                    "DeleteTeamInviteAction",
                    f"INVITE REMOVED -> {dto.email} from {org}/{dto.team_name}"
                )
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "email": dto.email,
                        "result": result
                    }
                )
            except Exception as e:
                log.error("DeleteTeamInviteAction", f"Failed to delete invite: {e}")
                raise

        except ValidationError as e:
            log.error("DeleteTeamInviteAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("DeleteTeamInviteAction", f"Failed to delete team invite: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to delete team invite: {e}"
            )
