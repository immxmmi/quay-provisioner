from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import TeamRepositoryPermission
from utils.logger import Logger as log


class SetTeamRepositoryPermissionAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = TeamRepositoryPermission(**data)
            log.info(
                "SetTeamRepositoryPermissionAction",
                f"IN -> org={org}, team={dto.team_name}, repo={dto.repository}, permission={dto.permission}"
            )

            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            if not GetTeamAction.exists(org, dto.team_name):
                return ActionResponse(
                    success=False,
                    message="Team does not exist",
                    data={"organization": org, "team": dto.team_name}
                )

            try:
                result = self.gateway.set_team_repository_permission(
                    organization=org,
                    team_name=dto.team_name,
                    repository=dto.repository,
                    permission=dto.permission
                )
                log.info(
                    "SetTeamRepositoryPermissionAction",
                    f"PERMISSION SET -> {org}/{dto.team_name} -> {dto.repository} ({dto.permission})"
                )
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "repository": dto.repository,
                        "permission": dto.permission,
                        "result": result
                    }
                )
            except Exception as e:
                log.error("SetTeamRepositoryPermissionAction", f"Failed to set permission: {e}")
                raise

        except ValidationError as e:
            log.error("SetTeamRepositoryPermissionAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("SetTeamRepositoryPermissionAction", f"Failed to manage team repository permission: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to manage team repository permission: {e}"
            )
