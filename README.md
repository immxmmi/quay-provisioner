# Pipeline Execution Platform

A Python-based automation tool for provisioning Red Hat Quay container registries using YAML-defined pipelines.

## Features

- **YAML-based Pipelines** - Define workflows declaratively
- **Dynamic Parameters** - Iterate over lists of organizations/robots
- **Idempotent Actions** - Safe to run multiple times (skips existing resources)
- **Debug Mode** - Shows CURL commands for manual API testing
- **Visual Output** - Progress bars, colored status, execution summary
- **Connection Pooling** - Efficient HTTP session reuse
- **Security** - Token masking in logs, URL encoding for path traversal prevention

## Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Connection

Edit `src/config/settings.yaml`:

```yaml
api:
  host: "http://127.0.0.1"
  port: 9080
  base_path: "/api/v1"

auth:
  token: "your-quay-api-token"
  type: "bearer"

debug:
  enabled: false

app:
  version: "2.2.1"
```

Or use environment variables:

```bash
export API_HOST="http://127.0.0.1"
export API_PORT="9080"
export API_TOKEN="your-token"
export DEBUG_ENABLED="true"
```

### 3. Define Your Resources

Edit `src/pipelines/inputs.yaml`:

```yaml
organizations:
  - name: "my-org"
    email: "admin@example.com"

robot_accounts:
  - organization: "my-org"
    robot_shortname: "ci-bot"
    description: "CI automation bot"
```

### 4. Run the Pipeline

```bash
# Using Makefile
make run

# Or directly
cd src && python main.py
```

## Makefile Commands

```bash
make help              # Show all available commands

# --- Development ---
make run               # Run the pipeline
make run-debug         # Run with debug output and CURL commands
make test              # Run syntax checks and unit tests
make lint              # Run linting with ruff
make lint-fix          # Auto-fix linting issues
make check             # Run all checks (lint + test)
make clean             # Remove cache files

# --- Quay Environment ---
make quay-up           # Start local Quay test environment
make quay-down         # Stop Quay test environment
make quay-logs         # Follow Quay logs
make quay-status       # Show Quay container status

# --- Docker ---
make build             # Build Docker image
make build TAG=1.0.0   # Build with custom version tag
make push TAG=1.0.0    # Push to registry
make run-container     # Run Docker container
make export            # Export image to tar file

# --- Info ---
make info              # Show current configuration
make info TAG=2.0.0    # Show config with custom tag
```

## Project Structure

```
PipelineExecutionPlatform/
├── src/
│   ├── main.py                    # Entry point
│   ├── exceptions.py              # Custom exception hierarchy
│   ├── config/
│   │   ├── loader.py              # Configuration singleton
│   │   └── settings.yaml          # API and auth settings
│   ├── pipelines/
│   │   ├── pipeline.yaml          # Pipeline definition
│   │   └── inputs.yaml            # Input data (orgs, robots)
│   ├── engine/
│   │   ├── pipeline_engine.py     # Pipeline orchestration
│   │   ├── pipeline_executor.py   # Step execution (injects QuayGateway per action)
│   │   └── action_registry.py     # Job-to-Action mapping
│   ├── engine_reader/
│   │   └── pipeline_reader.py     # YAML parsing
│   ├── gateway/
│   │   └── client.py              # HTTP client with pooling (shared by Quay gateway)
│   ├── quay/
│   │   ├── quay_gateway.py        # Quay-specific API wrapper
│   │   ├── actions/               # Quay action implementations
│   │   │   ├── base_action.py     # Gateway-agnostic base class
│   │   │   ├── organization/
│   │   │   ├── robot_account/
│   │   │   └── team/
│   │   └── model/                 # Domain models used by Quay actions
│   │       ├── organization_model.py
│   │       ├── robot_account_model.py
│   │       └── team_model.py
│   ├── model/                     # Shared Pydantic models
│   │   └── pipeline_model.py
│   └── utils/
│       ├── display.py             # Visual output (colors, progress)
│       └── logger.py              # Logging utilities
├── environment/
│   └── quay/
│       └── docker-compose.yaml    # Local Quay setup
├── Makefile
├── Dockerfile
├── requirements.txt
└── README.md
```

## Architecture Notes

- **Gateway layer**: `src/gateway/client.py` exposes a reusable HTTP client; `src/quay/quay_gateway.py` wraps Quay APIs and consumes that client.
- **Actions**: All Quay-specific actions now live under `src/quay/actions/...` and inherit from `BaseAction`, which only holds a gateway reference. This keeps the action logic agnostic and testable.
- **Execution**: `PipelineExecutor` instantiates a single `QuayGateway` and injects it into every action before calling `execute`, so swapping to another backend only requires providing a different gateway implementation and wiring it through the registry.
- **Models**: Quay domain models (organizations, teams, robots) sit under `src/quay/model/` while shared schemas like `PipelineDefinition` remain in `src/model/`, keeping reusable DTOs separate from backend-specific data.
- **Responses**: `ActionResponse` lives in `src/model/action_response.py` to keep the action output interface consistent for any executor or frontend component that needs to inspect results.

## Pipeline Configuration

### Pipeline Definition (`pipeline.yaml`)

```yaml
pipeline:
  # Step with dynamic iteration (loops over list)
  - name: create-organizations
    job: create_organization
    enabled: true
    params_list: "{{ organizations }}"

  # Step with static parameters
  - name: get-single-org
    job: get_organization
    enabled: false
    params:
      name: "my-org"

  # Another dynamic step
  - name: create-robot-accounts
    job: create_robot_account
    enabled: true
    params_list: "{{ robot_accounts }}"

  # Create teams in organizations
  - name: create-teams
    job: create_team
    enabled: true
    params_list: "{{ teams }}"

  # Add members to teams
  - name: add-team-members
    job: add_team_member
    enabled: true
    params_list: "{{ team_members }}"

  # Grant team repository permissions (optional)
  - name: set-team-repo-permissions
    job: set_team_repository_permission
    enabled: false
    params_list: "{{ team_repo_permissions }}"

  # Revoke repository permissions when teams should no longer access a repo
  - name: remove-team-repo-permissions
    job: remove_team_repository_permission
    enabled: false
    params_list: "{{ team_repo_permissions_to_remove }}"

  # Configure default permission prototypes (applied to future repositories)
  - name: set-default-repo-permissions
    job: set_default_repository_permission
    enabled: false
    params_list: "{{ default_repo_permissions }}"

  # Remove obsolete default permission prototypes
  - name: remove-default-repo-permissions
    job: remove_default_repository_permission
    enabled: false
    params_list: "{{ default_repo_permissions_to_remove }}"

  # Sync teams with LDAP groups (optional)
  - name: sync-teams-ldap
    job: sync_team_ldap
    enabled: false
    params_list: "{{ team_ldap_sync }}"

  # Invite workspace members by email
  - name: invite-team-members
    job: invite_team_member
    enabled: false
    params_list: "{{ team_member_invites }}"

  # Revoke outstanding invites
  - name: delete-team-invites
    job: delete_team_invite
    enabled: false
    params_list: "{{ team_invites_to_remove }}"

  # Remove stale team members
  - name: remove-team-members
    job: remove_team_member
    enabled: false
    params_list: "{{ team_members_to_remove }}"

  # Disable LDAP sync for a team
  - name: disable-team-ldap-sync
    job: unsync_team_ldap
    enabled: false
    params_list: "{{ team_ldap_unsync }}"

  # Inspect LDAP sync status
  - name: get-team-ldap-sync-status
    job: get_team_sync_status
    enabled: false
    params_list: "{{ team_sync_status }}"
```

### Input Data (`inputs.yaml`)

```yaml
organizations:
  - name: "production"
    email: "ops@company.com"
  - name: "staging"
    email: "dev@company.com"

robot_accounts:
  - organization: "production"
    robot_shortname: "deploy-bot"
    description: "Production deployment automation"
  - organization: "staging"
    robot_shortname: "ci-runner"
    description: "CI/CD pipeline runner"

teams:
  - organization: "production"
    team_name: "ops-team"
    role: "admin"
    description: "Operations team with full access"
  - organization: "production"
    team_name: "developers"
    role: "creator"
    description: "Development team"
  - organization: "staging"
    team_name: "qa-team"
    role: "member"
    description: "QA read-only access"

team_members:
  - organization: "production"
    team_name: "ops-team"
    member_name: "admin"
  - organization: "production"
    team_name: "developers"
    member_name: "dev-user1"
  - organization: "production"
    team_name: "developers"
    member_name: "dev-user2"
  - organization: "production"
    team_name: "developers"
    member_name: "production+ci-bot"

# Use `organization+robotname` when adding robot accounts as team members so the pipeline calls the proper API path.

# Configure repository permissions that teams need
team_repo_permissions:
  - organization: "production"
    team_name: "developers"
    repository: "production/dev-app"
    permission: "write"

# Revoke outdated permissions before rotating access
team_repo_permissions_to_remove:
  - organization: "production"
    team_name: "viewers"
    repository: "production/old-app"

# Optional: grant default permissions via permission prototypes on the organization
# The `delegate` block mirrors the Quay prototype payload (kind=team|user, name=entity).
default_repo_permissions:
  - organization: "production"
    delegate:
      kind: "team"
      name: "developers"
    role: "write"

# Optional: revoke prototype entries when defaults should change
default_repo_permissions_to_remove:
  - organization: "production"
    delegate:
      kind: "team"
      name: "viewers"
    role: "read"

# Optional: LDAP Team Sync (requires LDAP configured in Quay)
team_ldap_sync:
  - organization: "production"
    team_name: "ops-team"
    group_dn: "cn=ops,ou=groups,dc=company,dc=com"

# Optional: remove team members that should no longer have access
team_members_to_remove:
  - organization: "production"
    team_name: "viewers"
    member_name: "admin"

# Optional: disable LDAP sync once the team should no longer follow a group
team_ldap_unsync:
  - organization: "production"
    team_name: "viewers"

# Optional: check the current LDAP sync configuration for auditing
team_sync_status:
  - organization: "production"
    team_name: "ops-team"

# Optional: invite users by email to a team
team_member_invites:
  - organization: "production"
    team_name: "qa-team"
    email: "new-tester@example.com"

# Optional: cancel pending invites
team_invites_to_remove:
  - organization: "production"
    team_name: "staging"
    email: "old-invite@example.com"
```

## Available Actions

### Organization Actions

| Job Name              | Description               | Required Parameters        |
|-----------------------|---------------------------|----------------------------|
| `create_organization` | Create a new organization | `name`, `email` (optional) |
| `delete_organization` | Delete an organization    | `name`                     |
| `get_organization`    | Get organization details  | `name`                     |
| `list_organizations`  | List all organizations    | -                          |

### Robot Account Actions

| Job Name               | Description               | Required Parameters                                         |
|------------------------|---------------------------|-------------------------------------------------------------|
| `create_robot_account` | Create a robot account    | `organization`, `robot_shortname`, `description` (optional) |
| `delete_robot_account` | Delete a robot account    | `organization`, `robot_shortname`                           |
| `get_robot_account`    | Get robot account details | `organization`, `robot_shortname`                           |
| `list_robot_accounts`  | List robots in an org     | `organization`                                              |

### Team Actions

| Job Name          | Description              | Required Parameters                                                        |
|-------------------|--------------------------|----------------------------------------------------------------------------|
| `create_team`     | Create a team            | `organization`, `team_name`, `role` (member/creator/admin), `description`  |
| `delete_team`     | Delete a team            | `organization`, `team_name`                                                |
| `get_team`        | Get team and members     | `organization`, `team_name`                                                |
| `add_team_member` | Add a member to a team   | `organization`, `team_name`, `member_name`                                 |
| `sync_team_ldap`  | Sync team with LDAP group| `organization`, `team_name`, `group_dn`                                    |
| `set_team_repository_permission` | Assign repository permission to a team | `organization`, `team_name`, `repository`, `permission` |
| `remove_team_repository_permission` | Revoke repository permission from a team | `organization`, `team_name`, `repository` |
| `set_default_repository_permission` | Create a permission prototype (`POST /prototypes`) for the provided delegate | `organization`, `delegate`, `role` |
| `remove_default_repository_permission` | Delete matching prototypes (`DELETE /prototypes/{id}`) | `organization`, `delegate`, `role` |
| `invite_team_member` | Invite a user via email to a team | `organization`, `team_name`, `email` |
| `delete_team_invite` | Delete a pending invite | `organization`, `team_name`, `email` |
| `remove_team_member` | Remove a member from a team | `organization`, `team_name`, `member_name`                                 |
| `unsync_team_ldap`   | Disable LDAP sync for team | `organization`, `team_name`                                                |
| `get_team_sync_status` | Report LDAP sync status | `organization`, `team_name`                                                |

These actions mirror the [Quay Managing Teams API](https://docs.redhat.com/en/documentation/red_hat_quay/3.15/html/red_hat_quay_api_guide/quay-api-examples#managing-teams-api) plus the “Managing team members and repository permissions” subsection (6.19.1) and the “Default permissions” panel (6.19.2), so the pipeline can drive every supported endpoint for team membership, invitations, repository permissions, default repository permissions, and LDAP sync.

#### Team Roles

| Role      | Description                                      |
|-----------|--------------------------------------------------|
| `member`  | Read-only access to repositories                 |
| `creator` | Can create new repositories                      |
| `admin`   | Full admin access (manage team members, repos)   |

#### LDAP Team Sync

Teams can be synchronized with LDAP groups. When enabled, team membership is automatically managed based on LDAP group membership.

**Requirements:**
- LDAP must be configured in Quay
- The LDAP group DN must exist and be accessible

**Example:**
```yaml
team_ldap_sync:
  - organization: "my-org"
    team_name: "developers"
    group_dn: "cn=developers,ou=groups,dc=example,dc=com"
```

## Debug Mode

Enable debug mode to see detailed logs and CURL commands:

```bash
# Via Makefile
make run-debug

# Via environment variable
DEBUG_ENABLED=true python main.py

# Or in settings.yaml
debug:
  enabled: true
```

**Debug Output Example:**

```
API: POST /organization

┌─ CURL Command ─────────────────────────
│ curl -X POST \
      -H 'Content-Type: application/json' \
      -H 'Authorization: $API_TOKEN' \
      -d '{"name": "my-org", "email": "admin@example.com"}' \
      'http://127.0.0.1:9080/api/v1/organization'
└────────────────────────────────────────
```

Copy and run the CURL command manually to debug API issues.

## Docker

### Build Image

```bash
# Default version
make build

# Custom version
make build TAG=1.0.0

# Offline build (uses wheelhouse)
make build-offline TAG=1.0.0
```

### Run Container

```bash
# With custom pipeline files
docker run --rm -it \
  --network host \
  -v $(pwd)/src/pipelines:/app/pipelines \
  -e API_TOKEN="your-token" \
  quay-provisioner:1.0.0
```

### Push to Registry

```bash
make push TAG=1.0.0 REGISTRY=ghcr.io NAMESPACE=myuser
# Pushes: ghcr.io/myuser/quay-provisioner:1.0.0
```

## Local Development

### Setup Local Quay

```bash
# Start Quay + PostgreSQL + Redis
make quay-up

# Access Quay at http://127.0.0.1:9080
# Default credentials depend on your docker-compose setup

# View logs
make quay-logs

# Stop
make quay-down
```

### Run Tests

```bash
# All checks
make check

# Only tests
make test

# Only lint
make lint

# Auto-fix lint issues
make lint-fix
```

### Test Output

```
=== Syntax Check ===
✓ Syntax check passed

=== Import Tests ===
✓ exceptions
✓ base_action
✓ actions
✓ config
✓ gateway
✓ engine

=== Unit Tests ===
✓ Config singleton
✓ Header masking
✓ URL encoding

=== All tests passed! ===
```

## Configuration Reference

### Environment Variables

| Variable             | Description                     | Default                   |
|----------------------|---------------------------------|---------------------------|
| `API_HOST`           | Quay API host                   | from settings.yaml        |
| `API_PORT`           | Quay API port                   | from settings.yaml        |
| `API_TOKEN`          | Authentication token            | from settings.yaml        |
| `API_AUTH_TYPE`      | Auth type (bearer/basic/apikey) | `bearer`                  |
| `DEBUG_ENABLED`      | Enable debug logging            | `false`                   |
| `SHOW_CURL`          | Show CURL commands              | `false`                   |
| `PIPELINE_FILE`      | Path to pipeline.yaml           | `pipelines/pipeline.yaml` |
| `API_TIMEOUT`        | Request timeout (seconds)       | `30`                      |
| `DISABLE_TLS_VERIFY` | Disable TLS verification        | `false`                   |

### Auth Types

```yaml
# Bearer Token
auth:
  type: "bearer"
  token: "your-oauth-token"

# Basic Auth
auth:
  type: "basic"
  token: "base64-encoded-user:pass"

# API Key
auth:
  type: "apikey"
  token: "your-api-key"
```

## Quay API Reference

### Organizations

| Method | Endpoint                      | Description         |
|--------|-------------------------------|---------------------|
| POST   | `/api/v1/organization/`       | Create organization |
| GET    | `/api/v1/organization/{name}` | Get organization    |
| DELETE | `/api/v1/organization/{name}` | Delete organization |

### Robot Accounts

| Method | Endpoint                                    | Description         |
|--------|---------------------------------------------|---------------------|
| PUT    | `/api/v1/organization/{org}/robots/{robot}` | Create/update robot |
| GET    | `/api/v1/organization/{org}/robots/{robot}` | Get robot           |
| DELETE | `/api/v1/organization/{org}/robots/{robot}` | Delete robot        |
| GET    | `/api/v1/organization/{org}/robots/`        | List all robots     |

### Teams

| Method | Endpoint                                              | Description         |
|--------|-------------------------------------------------------|---------------------|
| PUT    | `/api/v1/organization/{org}/team/{team}`              | Create/update team  |
| GET    | `/api/v1/organization/{org}/team/{team}/members`      | Get team members    |
| DELETE | `/api/v1/organization/{org}/team/{team}`              | Delete team         |
| PUT    | `/api/v1/organization/{org}/team/{team}/members/{member}` | Add team member |
| POST   | `/api/v1/organization/{org}/team/{team}/syncing`      | Enable LDAP sync    |
| DELETE | `/api/v1/organization/{org}/team/{team}/syncing`      | Disable LDAP sync   |
| GET    | `/api/v1/organization/{org}/team/{team}/syncing`      | Get LDAP sync status|

## Troubleshooting

### "Connection refused"

```bash
# Check if Quay is running
make quay-status

# Check API endpoint
curl http://127.0.0.1:9080/api/v1/discovery
```

### "401 Unauthorized"

```bash
# Verify token is set
echo $API_TOKEN

# Test manually
curl -H "Authorization: Bearer $API_TOKEN" \
     http://127.0.0.1:9080/api/v1/organization/
```

### "Redirect loses port"

This is handled automatically. The client fixes redirects that lose the port number.

### "Robot already exists"

This is not an error - the pipeline is idempotent. Existing resources are skipped.
