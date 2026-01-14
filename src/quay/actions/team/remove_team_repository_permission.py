from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from .get_team import GetTeamAction
from exceptions import ValidationError
from model.action_response import ActionResponse
from quay.model.team_model import RemoveTeamRepositoryPermission
from utils.logger import Logger as log


class RemoveTeamRepositoryPermissionAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = RemoveTeamRepositoryPermission(**data)
            log.info(
                "RemoveTeamRepositoryPermissionAction",
                f"IN -> org={org}, team={dto.team_name}, repo={dto.repository}"
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
                result = self.gateway.remove_team_repository_permission(
                    organization=org,
                    team_name=dto.team_name,
                    repository=dto.repository
                )
                log.info(
                    "RemoveTeamRepositoryPermissionAction",
                    f"PERMISSION REMOVED -> {org}/{dto.team_name} -> {dto.repository}"
                )
                return ActionResponse(
                    success=True,
                    data={
                        "organization": org,
                        "team": dto.team_name,
                        "repository": dto.repository,
                        "result": result
                    }
                )
            except Exception as e:
                response = getattr(e, "response", None)
                status_code = getattr(response, "status_code", None)
                error_msg = str(e)
                if response is not None:
                    try:
                        text = response.text
                        if text:
                            error_msg = text
                    except Exception:
                        pass

                if status_code == 404 or "not found" in error_msg.lower():
                    log.info("RemoveTeamRepositoryPermissionAction", f"Permission already absent: {dto.repository}")
                    return ActionResponse(
                        success=True,
                        message="Permission already absent from repository",
                        data={
                            "organization": org,
                            "team": dto.team_name,
                            "repository": dto.repository
                        }
                    )
                raise

        except ValidationError as e:
            log.error("RemoveTeamRepositoryPermissionAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("RemoveTeamRepositoryPermissionAction", f"Failed to remove team repository permission: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to remove team repository permission: {e}"
            )
