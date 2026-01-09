from urllib.parse import quote

from exceptions import (
    RobotNotFoundError,
    RobotAlreadyExistsError,
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
