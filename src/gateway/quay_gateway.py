from gateway.client import ApiClient


class QuayGateway:
    def __init__(self, client=None):
        self.client = client or ApiClient()

    def create_organization(self, name: str):
        payload = {"name": name}
        return self.client.post("/organization/", json=payload)

    def delete_organization(self, name: str):
        return self.client.delete(f"/organization/{name}")

    def get_organization(self, name: str):
        return self.client.get(f"/organization/{name}")

    def list_organizations(self):
        return self.client.get("/organization/")

    def create_robot_account(self, organization: str, robot_shortname: str, description: str | None = None):
        payload = {"description": description}
        return self.client.put(
            f"/organization/{organization}/robots/{robot_shortname}",
            json=payload
        )

    def delete_robot_account(self, organization: str, robot_shortname: str):
        return self.client.delete(f"/organization/{organization}/robots/{robot_shortname}")

    def get_robot_account(self, organization: str, robot_shortname: str):
        return self.client.get(f"/organization/{organization}/robots/{robot_shortname}")

    def list_robot_accounts(self, organization: str):
        return self.client.get(f"/organization/{organization}/robots/")
