from actions.create_organization import CreateOrganizationAction
from actions.delete_organization import DeleteOrganizationAction
from actions.get_organization import GetOrganizationAction
from actions.list_organizations import ListOrganizationsAction
from actions.create_robot_account import CreateRobotAccountAction
from actions.delete_robot_account import DeleteRobotAccountAction
from actions.list_robot_accounts import ListRobotAccountsAction
from actions.get_robot_account import GetRobotAccountAction

ACTION_REGISTRY = {
    "create_organization": CreateOrganizationAction,
    "delete_organization": DeleteOrganizationAction,
    "get_organization": GetOrganizationAction,
    "list_organizations": ListOrganizationsAction,
    "create_robot_account": CreateRobotAccountAction,
    "delete_robot_account": DeleteRobotAccountAction,
    "list_robot_accounts": ListRobotAccountsAction,
    "get_robot_account": GetRobotAccountAction,
}