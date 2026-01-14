from urllib.parse import quote

from quay.exceptions import (
    RobotNotFoundError,
    RobotAlreadyExistsError,
    TeamNotFoundError,
    TeamAlreadyExistsError,
    QuayApiError,
)
from gateway.client import ApiClient
from utils.logger import Logger as log


def _safe_path(value: str) -> str:
    """URL-encode a path segment to prevent path traversal."""
    return quote(value, safe="")


class QuayGateway:
    def __init__(self, client=None):
        self.client = client or ApiClient()

    def create_organization(self, name: str, email: str = None):
        payload = {"name": name}
        if email:
            payload["email"] = email
        log.debug("QuayGateway", f"create_organization name={name} email={email}")
        return self.client.post("/organization/", json=payload)

    def delete_organization(self, name: str):
        log.debug("QuayGateway", f"delete_organization name={name}")
        return self.client.delete(f"/organization/{_safe_path(name)}")

    def get_organization(self, name: str):
        log.debug("QuayGateway", f"get_organization name={name}")
        return self.client.get(f"/organization/{_safe_path(name)}")

    def list_organizations(self):
        log.debug("QuayGateway", "list_organizations")
        return self.client.get("/organization")

    def create_robot_account(self, organization: str, robot_shortname: str, description: str | None = None):
        payload = {"description": description}
        log.debug("QuayGateway", f"create_robot_account org={organization} robot={robot_shortname}")
        safe_org = _safe_path(organization)
        safe_robot = _safe_path(robot_shortname)
        try:
            return self.client.put(
                f"/organization/{safe_org}/robots/{safe_robot}",
                json=payload
            )
        except Exception as e:
            # Check both exception message and response body (if available)
            msg = str(e)
            response_body = ""
            if hasattr(e, "response") and e.response is not None:
                try:
                    response_body = e.response.text
                except Exception:
                    pass

            full_msg = f"{msg} {response_body}"

            if "Existing robot with name" in full_msg:
                raise RobotAlreadyExistsError(
                    f"Robot {robot_shortname} already exists in {organization}",
                    response_body=response_body
                ) from e
            if "Could not find robot" in full_msg:
                # Pre-check failed but creation might still succeed
                return {
                    "created": True,
                    "robot": f"{organization}+{robot_shortname}",
                    "reason": "precheck_missing"
                }
            raise QuayApiError(f"Failed to create robot: {msg}") from e

    def delete_robot_account(self, organization: str, robot_shortname: str):
        log.debug("QuayGateway", f"delete_robot_account org={organization} robot={robot_shortname}")
        safe_org = _safe_path(organization)
        safe_robot = _safe_path(robot_shortname)
        return self.client.delete(f"/organization/{safe_org}/robots/{safe_robot}")

    def get_robot_account(self, organization: str, robot_shortname: str):
        log.debug("QuayGateway", f"get_robot_account org={organization} robot={robot_shortname}")
        safe_org = _safe_path(organization)
        safe_robot = _safe_path(robot_shortname)
        result = self.client.get(f"/organization/{safe_org}/robots/{safe_robot}")
        if result is None:
            raise RobotNotFoundError(
                f"Robot {robot_shortname} not found in {organization}",
                status_code=404
            )
        return result

    def list_robot_accounts(self, organization: str):
        log.debug("QuayGateway", f"list_robot_accounts org={organization}")
        safe_org = _safe_path(organization)
        return self.client.get(f"/organization/{safe_org}/robots/")

    # --- TEAM OPERATIONS ---

    def create_team(self, organization: str, team_name: str, role: str = "member", description: str | None = None):
        payload = {"role": role}
        if description:
            payload["description"] = description
        log.debug("QuayGateway", f"create_team org={organization} team={team_name} role={role}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        try:
            return self.client.put(
                f"/organization/{safe_org}/team/{safe_team}",
                json=payload
            )
        except Exception as e:
            msg = str(e)
            response_body = ""
            if hasattr(e, "response") and e.response is not None:
                try:
                    response_body = e.response.text
                except Exception:
                    pass

            full_msg = f"{msg} {response_body}"

            if "Team already exists" in full_msg or "already exists" in full_msg.lower():
                raise TeamAlreadyExistsError(
                    f"Team {team_name} already exists in {organization}",
                    response_body=response_body
                ) from e
            raise QuayApiError(f"Failed to create team: {msg}") from e

    def get_team(self, organization: str, team_name: str):
        log.debug("QuayGateway", f"get_team org={organization} team={team_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        result = self.client.get(f"/organization/{safe_org}/team/{safe_team}/members")
        if result is None:
            raise TeamNotFoundError(
                f"Team {team_name} not found in {organization}",
                status_code=404
            )
        return result

    def delete_team(self, organization: str, team_name: str):
        log.debug("QuayGateway", f"delete_team org={organization} team={team_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        return self.client.delete(f"/organization/{safe_org}/team/{safe_team}")

    def add_team_member(self, organization: str, team_name: str, member_name: str):
        log.debug("QuayGateway", f"add_team_member org={organization} team={team_name} member={member_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_member = _safe_path(member_name)
        return self.client.put(f"/organization/{safe_org}/team/{safe_team}/members/{safe_member}")

    def remove_team_member(self, organization: str, team_name: str, member_name: str):
        log.debug("QuayGateway", f"remove_team_member org={organization} team={team_name} member={member_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_member = _safe_path(member_name)
        return self.client.delete(f"/organization/{safe_org}/team/{safe_team}/members/{safe_member}")

    def invite_team_member(self, organization: str, team_name: str, email: str):
        log.debug("QuayGateway", f"invite_team_member org={organization} team={team_name} email={email}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_email = quote(email, safe="")
        return self.client.put(f"/organization/{safe_org}/team/{safe_team}/invite/{safe_email}")

    def delete_team_invite(self, organization: str, team_name: str, email: str):
        log.debug("QuayGateway", f"delete_team_invite org={organization} team={team_name} email={email}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_email = quote(email, safe="")
        return self.client.delete(f"/organization/{safe_org}/team/{safe_team}/invite/{safe_email}")

    def set_team_repository_permission(
        self,
        organization: str,
        team_name: str,
        repository: str,
        permission: str = "read"
    ):
        log.debug(
            "QuayGateway",
            f"set_team_repository_permission org={organization} team={team_name} repo={repository} permission={permission}"
        )
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_repo = _safe_path(repository)
        payload = {"permission": permission}
        return self.client.put(
            f"/organization/{safe_org}/team/{safe_team}/repositories/{safe_repo}",
            json=payload
        )

    def remove_team_repository_permission(self, organization: str, team_name: str, repository: str):
        log.debug("QuayGateway", f"remove_team_repository_permission org={organization} team={team_name} repo={repository}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        safe_repo = _safe_path(repository)
        return self.client.delete(f"/organization/{safe_org}/team/{safe_team}/repositories/{safe_repo}")

    def list_prototypes(self, organization: str):
        log.debug("QuayGateway", f"list_prototypes org={organization}")
        safe_org = _safe_path(organization)
        return self.client.get(f"/organization/{safe_org}/prototypes")

    def set_default_repository_permission(
        self,
        organization: str,
        delegate: dict,
        role: str,
        activating_user: str | None = None
    ):
        log.debug(
            "QuayGateway",
            f"set_default_repository_permission org={organization} delegate={delegate} role={role} user={activating_user}"
        )
        safe_org = _safe_path(organization)
        payload = {"delegate": delegate, "role": role}
        if activating_user:
            payload["activating_user"] = {"name": activating_user}
        return self.client.post(
            f"/organization/{safe_org}/prototypes",
            json=payload
        )

    def delete_prototype(self, organization: str, prototype_id: str):
        log.debug("QuayGateway", f"delete_prototype org={organization} prototype_id={prototype_id}")
        safe_org = _safe_path(organization)
        safe_id = _safe_path(str(prototype_id))
        return self.client.delete(f"/organization/{safe_org}/prototypes/{safe_id}")

    def sync_team_ldap(self, organization: str, team_name: str, group_dn: str):
        """Enable LDAP sync for a team with the specified LDAP group DN."""
        payload = {"group_dn": group_dn}
        log.debug("QuayGateway", f"sync_team_ldap org={organization} team={team_name} group_dn={group_dn}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        return self.client.post(f"/organization/{safe_org}/team/{safe_team}/syncing", json=payload)

    def unsync_team_ldap(self, organization: str, team_name: str):
        """Disable LDAP sync for a team."""
        log.debug("QuayGateway", f"unsync_team_ldap org={organization} team={team_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        return self.client.delete(f"/organization/{safe_org}/team/{safe_team}/syncing")

    def get_team_sync_status(self, organization: str, team_name: str):
        """Get LDAP sync status for a team."""
        log.debug("QuayGateway", f"get_team_sync_status org={organization} team={team_name}")
        safe_org = _safe_path(organization)
        safe_team = _safe_path(team_name)
        return self.client.get(f"/organization/{safe_org}/team/{safe_team}/syncing")
