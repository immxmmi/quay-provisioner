from actions.base_action import BaseAction
from actions.get_organization import GetOrganizationAction
from actions.get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from model.team_model import AddTeamMember
from utils.logger import Logger as log


class AddTeamMemberAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = AddTeamMember(**data)
            log.info("AddTeamMemberAction", f"IN -> org={org}, team={dto.team_name}, member={dto.member_name}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- VALIDATE TEAM ---
            if not GetTeamAction.exists(org, dto.team_name):
                return ActionResponse(
                    success=False,
                    message="Team does not exist",
                    data={"organization": org, "team": dto.team_name}
                )

            # --- ADD MEMBER ---
            result = self.gateway.add_team_member(org, dto.team_name, dto.member_name)
            log.info("AddTeamMemberAction", f"ADDED -> {dto.member_name} to {org}/{dto.team_name}")

            return ActionResponse(
                success=True,
                data={
                    "organization": org,
                    "team": dto.team_name,
                    "member": dto.member_name,
                    "result": result
                }
            )

        except ValidationError as e:
            log.error("AddTeamMemberAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("AddTeamMemberAction", f"Failed to add team member: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to add team member: {e}"
            )
