from ..base_action import BaseAction
from ..organization.get_organization import GetOrganizationAction
from exceptions import ValidationError
from quay.exceptions import TeamAlreadyExistsError
from model.action_response import ActionResponse
from quay.model.team_model import CreateTeam
from utils.logger import Logger as log


class CreateTeamAction(BaseAction):

    def execute(self, data: dict) -> ActionResponse:
        try:
            self.validate_required(data, "organization")
            org = data["organization"]

            dto = CreateTeam(**data)
            log.info("CreateTeamAction", f"IN -> org={org}, team={dto.team_name}, role={dto.role}")

            # --- VALIDATE ORG ---
            if not GetOrganizationAction.exists(org):
                return ActionResponse(
                    success=False,
                    message="Organization does not exist",
                    data={"organization": org}
                )

            # --- CREATE ---
            try:
                result = self.gateway.create_team(
                    organization=org,
                    team_name=dto.team_name,
                    role=dto.role,
                    description=dto.description
                )
                log.info("CreateTeamAction", f"CREATED -> {org}/{dto.team_name}")

                return ActionResponse(
                    success=True,
                    data={"organization": org, "team": dto.team_name, "role": dto.role, "result": result}
                )

            except TeamAlreadyExistsError:
                log.info("CreateTeamAction", f"Team already exists: {dto.team_name}")
                return ActionResponse(
                    success=True,
                    message="Team already exists",
                    data={"organization": org, "team": dto.team_name}
                )

        except ValidationError as e:
            log.error("CreateTeamAction", f"Validation error: {e}")
            return ActionResponse(success=False, message=str(e))

        except Exception as e:
            log.error("CreateTeamAction", f"Failed to create team: {e}")
            return ActionResponse(
                success=False,
                message=f"Failed to create team: {e}"
            )
