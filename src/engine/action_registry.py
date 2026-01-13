from actions.add_team_member import AddTeamMemberAction
from actions.create_organization import CreateOrganizationAction
from actions.create_robot_account import CreateRobotAccountAction
from actions.create_team import CreateTeamAction
from actions.delete_organization import DeleteOrganizationAction
from actions.delete_robot_account import DeleteRobotAccountAction
from actions.delete_team import DeleteTeamAction
from actions.get_organization import GetOrganizationAction
from actions.get_robot_account import GetRobotAccountAction
from actions.get_team import GetTeamAction
from actions.list_organizations import ListOrganizationsAction
from actions.list_robot_accounts import ListRobotAccountsAction
from actions.sync_team_ldap import SyncTeamLdapAction

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
    "sync_team_ldap": SyncTeamLdapAction,
}
