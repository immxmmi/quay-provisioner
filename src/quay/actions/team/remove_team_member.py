from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import RemoveTeamMember
from utils.logger import Logger as log


class RemoveTeamMemberAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = RemoveTeamMember(**data)
            log.info("RemoveTeamMemberAction", f"IN -> org={org}, team={dto.team_name}, member={dto.member_name}")

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

            # --- REMOVE MEMBER ---
            try:
                result = self.gateway.remove_team_member(org, dto.team_name, dto.member_name)
                log.info("RemoveTeamMemberAction", f"REMOVED -> {dto.member_name} from {org}/{dto.team_name}")
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "member": dto.member_name,
                        "result": result
                    }
                )
            except Exception as e:
                response = getattr(e, "response", None)
                status_code = getattr(response, "status_code", None)
                error_msg = str(e)
                if response is not None:
                    try:
                        body_text = response.text
                        if body_text:
                            error_msg = body_text
                    except Exception:
                        pass

                if status_code == 404 or "not a member" in error_msg.lower():
                    log.info("RemoveTeamMemberAction", f"Member not in team: {dto.member_name}")
                    return ActionResponse(
                        success=True,
                        message="Member not present in team",
                        data={
                            "organization": org,
                            "team": dto.team_name,
                            "member": dto.member_name
                        }
                    )
                raise

        except ValidationError as e:
            log.error("RemoveTeamMemberAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("RemoveTeamMemberAction", f"Failed to remove team member: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to remove team member: {e}"
            )
