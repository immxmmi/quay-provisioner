from actions.base_action import BaseAction
from actions.get_organization import GetOrganizationAction
from actions.get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from model.team_model import SyncTeamLdap
from utils.logger import Logger as log


class SyncTeamLdapAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = SyncTeamLdap(**data)
            log.info("SyncTeamLdapAction", f"IN -> org={org}, team={dto.team_name}, group_dn={dto.group_dn}")

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

            # --- CHECK IF ALREADY SYNCED ---
            try:
                sync_status = self.gateway.get_team_sync_status(org, dto.team_name)
                if sync_status and sync_status.get("group_dn") == dto.group_dn:
                    log.info("SyncTeamLdapAction", f"Team already synced with same group_dn: {dto.group_dn}")
                    return ActionResponse(
                        success=True,
                        message="Team already synced with LDAP group",
                        data={
                            "organization": org,
                            "team": dto.team_name,
                            "group_dn": dto.group_dn
                        }
                    )
            except Exception:
                # Not synced yet, continue
                pass

            # --- SYNC WITH LDAP ---
            try:
                result = self.gateway.sync_team_ldap(org, dto.team_name, dto.group_dn)
                log.info("SyncTeamLdapAction", f"SYNCED -> {org}/{dto.team_name} with {dto.group_dn}")

                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "group_dn": dto.group_dn,
                        "result": result
                    }
                )
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, "response") and e.response is not None:
                    try:
                        error_msg = e.response.text
                    except Exception:
                        pass

                # Handle already synced case
                if "already synced" in error_msg.lower() or "already enabled" in error_msg.lower():
                    log.info("SyncTeamLdapAction", f"Team already synced: {dto.team_name}")
                    return ActionResponse(
                        success=True,
                        message="Team already synced with LDAP",
                        data={
                            "organization": org,
                            "team": dto.team_name,
                            "group_dn": dto.group_dn
                        }
                    )
                raise

        except ValidationError as e:
            log.error("SyncTeamLdapAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("SyncTeamLdapAction", f"Failed to sync team with LDAP: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to sync team with LDAP: {e}"
            )
