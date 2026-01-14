from quay.actions.team.add_team_member import AddTeamMemberAction
from quay.actions.organization.create_organization import CreateOrganizationAction
from quay.actions.robot_account.create_robot_account import CreateRobotAccountAction
from quay.actions.team.create_team import CreateTeamAction
from quay.actions.organization.delete_organization import DeleteOrganizationAction
from quay.actions.robot_account.delete_robot_account import DeleteRobotAccountAction
from quay.actions.team.delete_team import DeleteTeamAction
from quay.actions.organization.get_organization import GetOrganizationAction
from quay.actions.robot_account.get_robot_account import GetRobotAccountAction
from quay.actions.team.get_team import GetTeamAction
from quay.actions.organization.list_organizations import ListOrganizationsAction
from quay.actions.robot_account.list_robot_accounts import ListRobotAccountsAction
from quay.actions.team.sync_team_ldap import SyncTeamLdapAction
from quay.actions.team.get_team_sync_status import GetTeamSyncStatusAction
from quay.actions.team.remove_team_member import RemoveTeamMemberAction
from quay.actions.team.unsync_team_ldap import UnsyncTeamLdapAction

ACTION_REGISTRY = {
    # Organization actions
    "create_organization": CreateOrganizationAction,
    "delete_organization": DeleteOrganizationAction,
    "get_organization": GetOrganizationAction,
    "list_organizations": ListOrganizationsAction,
    # Robot account actions
    "create_robot_account": CreateRobotAccountAction,
    "delete_robot_account": DeleteRobotAccountAction,
    "list_robot_accounts": ListRobotAccountsAction,
    "get_robot_account": GetRobotAccountAction,
    # Team actions
    "create_team": CreateTeamAction,
    "delete_team": DeleteTeamAction,
    "get_team": GetTeamAction,
    "add_team_member": AddTeamMemberAction,
    "remove_team_member": RemoveTeamMemberAction,
    "sync_team_ldap": SyncTeamLdapAction,
    "unsync_team_ldap": UnsyncTeamLdapAction,
    "get_team_sync_status": GetTeamSyncStatusAction,
}
