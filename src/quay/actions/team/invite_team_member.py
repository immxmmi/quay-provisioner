from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import InviteTeamMember
from utils.logger import Logger as log


class InviteTeamMemberAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = InviteTeamMember(**data)
            log.info(
                "InviteTeamMemberAction",
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
                result = self.gateway.invite_team_member(
                    organization=org,
                    team_name=dto.team_name,
                    email=dto.email
                )
                log.info(
                    "InviteTeamMemberAction",
                    f"INVITED -> {dto.email} to {org}/{dto.team_name}"
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
                log.error("InviteTeamMemberAction", f"Failed to invite member: {e}")
                raise

        except ValidationError as e:
            log.error("InviteTeamMemberAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("InviteTeamMemberAction", f"Failed to invite team member: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to invite team member: {e}"
            )
