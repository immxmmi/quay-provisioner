from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import RemoveDefaultRepositoryPermission
from utils.logger import Logger as log


class RemoveDefaultRepositoryPermissionAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = RemoveDefaultRepositoryPermission(**data)
            delegate_payload = dto.delegate.model_dump()
            log.info(
                "RemoveDefaultRepositoryPermissionAction",
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
            if isinstance(prototypes, dict) and "prototypes" in prototypes:
                items = prototypes["prototypes"] or []

            matches = []
            for entry in items:
                delegate = entry.get("delegate", {})
                if delegate.get("name") != dto.delegate.name or delegate.get("kind") != dto.delegate.kind:
                    continue
                if dto.role and entry.get("role") != dto.role:
                    continue
                proto_id = entry.get("id") or entry.get("prototypes_id")
                if proto_id is None:
                    continue
                matches.append(proto_id)

            if not matches:
                log.info("RemoveDefaultRepositoryPermissionAction", "No matching default permission prototypes found")
                return ActionResponse(
                    success=True,
                message="No matching default permission prototypes exist",
                data={"organization": org, "delegate": delegate_payload, "role": dto.role}
            )

            results = []
            for prototype_id in matches:
                delete_result = self.gateway.delete_prototype(org, prototype_id)
                results.append({"prototype_id": prototype_id, "result": delete_result})

            log.info(
                "RemoveDefaultRepositoryPermissionAction",
                f"DEFAULT PERMS REMOVED -> {org}/{dto.delegate.kind}/{dto.delegate.name} roles={dto.role or 'any'}"
            )
            return ActionResponse(
                success=True,
                data={
                    "organization": org,
                    "delegate": delegate_payload,
                    "role": dto.role,
                    "removed": results
                }
            )

        except ValidationError as e:
            log.error("RemoveDefaultRepositoryPermissionAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("RemoveDefaultRepositoryPermissionAction", f"Failed to remove default repository permission: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to remove default repository permission: {e}"
            )
