# Quay Provisioner Helm Chart

Helm chart for deploying the Quay Provisioner as a Kubernetes Job.

## Installation

```bash
# Add your values
helm install quay-provisioner ./helm \
  --namespace quay-system \
  --create-namespace \
  --set secrets.apiHost="https://quay.example.com" \
  --set secrets.apiToken="your-token"
```

## Configuration

### Quick Start Values

```yaml
# my-values.yaml
secrets:
  apiHost: "https://quay.example.com"
  apiPort: "443"
  apiToken: "your-quay-api-token"

pipelines:
  inputs:
    organizations:
      - name: my-org
        email: admin@example.com
    robot_accounts:
      - organization: my-org
        robot_shortname: ci-bot
        description: CI automation
```

```bash
helm install quay-provisioner ./helm -f my-values.yaml
```

### Using External Secret

```yaml
secrets:
  existingSecret: "my-external-secret"
  # Keys expected: API_HOST, API_PORT, API_BASE_PATH, API_AUTH_TYPE, API_TOKEN
```

### Enable Debug Mode

```yaml
settings:
  debug: true
  showCurl: true
```

### Custom CA Bundle

```yaml
caBundle:
  enabled: true
  configMapName: my-ca-bundle
  key: ca.crt
```

## Values Reference

| Parameter                     | Description           | Default                            |
|-------------------------------|-----------------------|------------------------------------|
| `image.repository`            | Container image       | `ghcr.io/immxmmi/quay-provisioner` |
| `image.tag`                   | Image tag             | `Chart.appVersion`                 |
| `secrets.apiHost`             | Quay API host         | `http://127.0.0.1`                 |
| `secrets.apiPort`             | Quay API port         | `443`                              |
| `secrets.apiToken`            | API token             | `""`                               |
| `secrets.existingSecret`      | Use existing secret   | `""`                               |
| `settings.debug`              | Enable debug mode     | `false`                            |
| `settings.showCurl`           | Show CURL commands    | `false`                            |
| `settings.disableTlsVerify`   | Disable TLS verify    | `false`                            |
| `job.backoffLimit`            | Job retry count       | `3`                                |
| `job.ttlSecondsAfterFinished` | Cleanup after seconds | `300`                              |
| `resources.limits.cpu`        | CPU limit             | `500m`                             |
| `resources.limits.memory`     | Memory limit          | `256Mi`                            |

## Pipeline Configuration

Define pipelines directly in values:

```yaml
pipelines:
  pipeline:
    - name: create-organizations
      job: create_organization
      enabled: true
      params_list: "{{ organizations }}"

    - name: create-robot-accounts
      job: create_robot_account
      enabled: true
      params_list: "{{ robot_accounts }}"

  inputs:
    organizations:
      - name: production
        email: ops@company.com
    robot_accounts:
      - organization: production
        robot_shortname: deploy-bot
        description: Deployment automation
```

## Monitoring

```bash
# Watch job status
kubectl get jobs -w

# View logs
kubectl logs job/quay-provisioner -f

# Check results
kubectl describe job/quay-provisioner
```

## Re-run Job

```bash
# Delete old job
kubectl delete job/quay-provisioner

# Reinstall
helm upgrade quay-provisioner ./helm
```
