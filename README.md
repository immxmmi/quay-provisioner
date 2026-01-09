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
│   │   ├── pipeline_executor.py   # Step execution
│   │   └── action_registry.py     # Job-to-Action mapping
│   ├── engine_reader/
│   │   └── pipeline_reader.py     # YAML parsing
│   ├── gateway/
│   │   ├── client.py              # HTTP client with pooling
│   │   └── quay_gateway.py        # Quay API wrapper
│   ├── actions/                   # Action implementations
│   │   ├── base_action.py         # Abstract base class
│   │   ├── create_organization.py
│   │   ├── delete_organization.py
│   │   ├── get_organization.py
│   │   ├── list_organizations.py
│   │   ├── create_robot_account.py
│   │   ├── delete_robot_account.py
│   │   ├── get_robot_account.py
│   │   └── list_robot_accounts.py
│   ├── model/                     # Pydantic models
│   │   ├── action_response.py
│   │   ├── organization_model.py
│   │   ├── robot_account_model.py
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
```

## Available Actions

| Job Name               | Description               | Required Parameters                                         |
|------------------------|---------------------------|-------------------------------------------------------------|
| `create_organization`  | Create a new organization | `name`, `email` (optional)                                  |
| `delete_organization`  | Delete an organization    | `name`                                                      |
| `get_organization`     | Get organization details  | `name`                                                      |
| `list_organizations`   | List all organizations    | -                                                           |
| `create_robot_account` | Create a robot account    | `organization`, `robot_shortname`, `description` (optional) |
| `delete_robot_account` | Delete a robot account    | `organization`, `robot_shortname`                           |
| `get_robot_account`    | Get robot account details | `organization`, `robot_shortname`                           |
| `list_robot_accounts`  | List robots in an org     | `organization`                                              |

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