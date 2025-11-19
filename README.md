<file name=0 path=README.md># PipelineExecutionPlatform – README

## Overview
The PipelineExecutionPlatform automates interactions with the Red Hat Quay API using YAML‑defined pipelines.  
It reads input data, maps it to pipeline steps, and executes actions like creating organizations or robot accounts.

## Structure
- `inputs.yaml` — defines organizations and robot accounts.
- `pipeline.yaml` — defines jobs and execution order.
- `ACTION_REGISTRY` — maps job names to Python Action classes.
- `QuayGateway` — handles all HTTP communication with the Quay API.

## Supported Actions

### Organizations
- `create_organization`
- `delete_organization`
- `get_organization`
- `list_organizations`

### Robot Accounts
- `create_robot_account`
- `delete_robot_account`
- `get_robot_account`
- `list_robot_accounts`

## Quay API
### Organization
- POST `/organization/`
- GET `/organization/<name>`
- DELETE `/organization/<name>`

### Robot Accounts
- PUT `/organization/<org>/robots/<robot>`
- GET `/organization/<org>/robots/<robot>`
- DELETE `/organization/<org>/robots/<robot>`
- GET `/organization/<org>/robots`

## Example Execution Flow
1. Engine loads the pipeline and inputs.
2. Each step is mapped to an Action.
3. Actions call Quay API via `QuayGateway`.
4. Outputs are printed to the console.


## Pipeline Example (`pipeline.yaml`)
```yaml
# pipelines/pipeline.yaml
input_file: "pipelines/inputs.yaml"

pipeline:
  - name: create-organizations
    job: create_organization
    enabled: true
    params_list: "{{ inputs.organizations }}"

  - name: create-robot-accounts
    job: create_robot_account
    enabled: true
    params_list: "{{ inputs.robot_accounts }}"
```

## Input Example (`inputs.yaml`)
```yaml
# pipelines/inputs.yaml
organizations:
  - name: "momo"
    visibility: "private"
    email: "momo@test.ch"
    owner: "momo"

  - name: "test"
    visibility: "public"
    email: "contact@org2.com"
    owner: "system"

robot_accounts:
  - organization: "momo"
    robot_shortname: "ci-bot"
    description: "CI automation bot"

  - organization: "momo"
    robot_shortname: "deployment"
    description: "Deployments bot"

  - organization: "test"
    robot_shortname: "scanner"
    description: "Security scan bot"
```