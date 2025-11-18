from gateway.quay_gateway import QuayGateway
from model.action_response import ActionResponse


class ListOrganizationsAction:
    def __init__(self, gateway=None):
        self.gateway = gateway or QuayGateway()

    def execute(self, data: dict) -> ActionResponse:
        try:
            print(f"[ListOrganizationsAction] Executing with data: {data}")
            result = self.gateway.list_organizations()
            print(f"[ListOrganizationsAction] API result: {result}")

            return ActionResponse(
                success=True,
                message="Organizations listed successfully",
                data={"result": result}
            )

        except Exception as e:
            return ActionResponse(
                success=False,
                message=str(e)
            )
