from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import TeamSyncStatusRequest
from utils.logger import Logger as log


class GetTeamSyncStatusAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = TeamSyncStatusRequest(**data)
            log.info("GetTeamSyncStatusAction", f"IN -> org={org}, team={dto.team_name}")

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

            # --- GET SYNC STATUS ---
            try:
                result = self.gateway.get_team_sync_status(org, dto.team_name)
                log.info("GetTeamSyncStatusAction", f"SYNC STATUS -> {org}/{dto.team_name}")
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "status": result
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
                    log.info("GetTeamSyncStatusAction", f"No LDAP sync configured for {dto.team_name}")
                    return ActionResponse(
                        success=True,
                        message="Team has no LDAP sync configured",
                        data={
                            "organization": org,
                            "team": dto.team_name
                        }
                    )
                raise

        except ValidationError as e:
            log.error("GetTeamSyncStatusAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("GetTeamSyncStatusAction", f"Failed to get team sync status: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to get team sync status: {e}"
            )
