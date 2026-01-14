from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import UnsyncTeamLdap
from utils.logger import Logger as log


class UnsyncTeamLdapAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = UnsyncTeamLdap(**data)
            log.info("UnsyncTeamLdapAction", f"IN -> org={org}, team={dto.team_name}")

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

            # --- UNSYNC LDAP ---
            try:
                result = self.gateway.unsync_team_ldap(org, dto.team_name)
                log.info("UnsyncTeamLdapAction", f"UNSYNCED -> {org}/{dto.team_name}")
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
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

                if status_code == 404 or "not synced" in error_msg.lower():
                    log.info("UnsyncTeamLdapAction", f"Team not synced: {dto.team_name}")
                    return ActionResponse(
                        success=True,
                        message="Team was not synced with LDAP",
                        data={
                            "organization": org,
                            "team": dto.team_name
                        }
                    )
                raise

        except ValidationError as e:
            log.error("UnsyncTeamLdapAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("UnsyncTeamLdapAction", f"Failed to unsync team from LDAP: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to unsync team from LDAP: {e}"
            )
