from gateway.client import ApiClient
from utils.logger import Logger as log


class QuayGateway:
    def __init__(self, client=None):
        self.client = client or ApiClient()

    def create_organization(self, name: str):
        payload = {"name": name}
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"create_organization name={name}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"create_organization args=({name},)")
        return self.client.post("/organization", json=payload)

    def delete_organization(self, name: str):
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"delete_organization name={name}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"delete_organization args=({name},)")
        return self.client.delete(f"/organization/{name}")

    def get_organization(self, name: str):
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"get_organization name={name}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"get_organization args=({name},)")
        return self.client.get(f"/organization/{name}")

    def list_organizations(self):
        if self.client.cfg.debug:
            log.debug("QuayGateway", "list_organizations")
        if self.client.cfg.debug:
            log.debug("QuayGateway", "list_organizations args=()")
        return self.client.get("/organization")

    def create_robot_account(self, organization: str, robot_shortname: str, description: str | None = None):
        payload = {"description": description}
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"create_robot_account org={organization} robot={robot_shortname} description={description}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"create_robot_account args=({organization}, {robot_shortname}, {description})")
        return self.client.put(
            f"/organization/{organization}/robots/{robot_shortname}",
            json=payload
        )

    def delete_robot_account(self, organization: str, robot_shortname: str):
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"delete_robot_account org={organization} robot={robot_shortname}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"delete_robot_account args=({organization}, {robot_shortname})")
        return self.client.delete(f"/organization/{organization}/robots/{robot_shortname}")

    def get_robot_account(self, organization: str, robot_shortname: str):
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"get_robot_account org={organization} robot={robot_shortname}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"get_robot_account args=({organization}, {robot_shortname})")
        return self.client.get(f"/organization/{organization}/robots/{robot_shortname}")

    def list_robot_accounts(self, organization: str):
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"list_robot_accounts org={organization}")
        if self.client.cfg.debug:
            log.debug("QuayGateway", f"list_robot_accounts args=({organization},)")
        return self.client.get(f"/organization/{organization}/robots/")
