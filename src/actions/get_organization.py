from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse
from model.organization_model import GetOrganization
from utils.logger import Logger as log


class GetOrganizationAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    @staticmethod
    def exists(name: str) -> bool:
        try:
            gateway = QuayGateway()
            result = gateway.get_organization(name)
            return result is not None
        except Exception as e:
            if "404" in str(e):  # NOT FOUND means it does not exist
                return False
            raise e

    def execute(self, data: dict) -> ActionResponse:
        try:
            log.info("GetOrganizationAction", f"Executing organization lookup request payload={data}")
            org = GetOrganization(**data)
            log.debug("GetOrganizationAction", f"Validated input mapped to model model={org.model_dump()}")
            log.info("GetOrganizationAction", f"Calling Quay API: get_organization name={org.name}")
            result = self.gateway.get_organization(org.name)
            log.info("GetOrganizationAction", f"Organization fetch succeeded name={org.name}")

            return ActionResponse(
                success=True,
                message="Organization fetched successfully",
                data={"organization": org.name, "result": result}
            )

        except Exception as e:
            log.error("GetOrganizationAction", f"Organization fetch failed error={e}")
            return ActionResponse(
                success=False,
                message=str(e)
            )
