from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import DefaultRepositoryPermission
from utils.logger import Logger as log


class SetDefaultRepositoryPermissionAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = DefaultRepositoryPermission(**data)
            delegate_payload = dto.delegate.model_dump()
            log.info(
                "SetDefaultRepositoryPermissionAction",
                f"IN -> org={org}, delegate={delegate_payload}, role={dto.role}"
            )

            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            prototypes = self.gateway.list_prototypes(org)
            items = prototypes or []
            if isinstance(prototypes, dict):
                items = prototypes.get("prototypes") or []

            duplicates = []
            for entry in items:
                delegate = entry.get("delegate", {})
                if delegate.get("name") != delegate_payload.get("name"):
                    continue
                if delegate.get("kind") != delegate_payload.get("kind"):
                    continue
                if entry.get("role") != dto.role:
                    continue
                proto_id = entry.get("id") or entry.get("prototypes_id")
                duplicates.append(proto_id or entry)

            if duplicates:
                log.info("SetDefaultRepositoryPermissionAction", "Default permission prototype already exists")
                return ActionResponse(
                    success=True,
                    message="Default permission prototype already exists",
                    data={
                        "organization": org,
                        "delegate": delegate_payload,
                        "role": dto.role,
                        "prototypes": duplicates
                    }
                )

            try:
                result = self.gateway.set_default_repository_permission(
                    organization=org,
                    delegate=delegate_payload,
                    role=dto.role,
                    activating_user=dto.activating_user
                )
                log.info(
                    "SetDefaultRepositoryPermissionAction",
                    f"DEFAULT PERM SET -> {org}/{dto.delegate.kind}/{dto.delegate.name} ({dto.role})"
                )
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "delegate": delegate_payload,
                        "role": dto.role,
                        "activating_user": dto.activating_user,
                        "result": result
                    }
                )
            except Exception as e:
                log.error("SetDefaultRepositoryPermissionAction", f"Failed to set default permission: {e}")
                raise

        except ValidationError as e:
            log.error("SetDefaultRepositoryPermissionAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("SetDefaultRepositoryPermissionAction", f"Failed to manage default repository permission: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to manage default repository permission: {e}"
            )
