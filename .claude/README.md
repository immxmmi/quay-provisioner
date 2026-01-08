# Pipeline Execution Platform - Projektnotizen

## Schnellübersicht

**Projekt:** Quay Provisioner
**Version:** 2.2.3
**Python:** 3.12
**Zweck:** Automatisiert Interaktionen mit der Red Hat Quay Container Registry API über YAML-definierte Pipelines

---

## Architektur

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Entry Point)                │
├─────────────────────────────────────────────────────────┤
│                  PipelineEngine (Orchestrator)          │
│  ┌──────────────┬──────────────┬──────────────────────┐ │
│  │   Reader     │  Validator   │     Executor         │ │
│  └──────────────┴──────────────┴──────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                   ACTION LAYER                          │
│  (8 Action-Klassen in ACTION_REGISTRY)                  │
├─────────────────────────────────────────────────────────┤
│                   GATEWAY LAYER                         │
│  (QuayGateway + ApiClient)                              │
├─────────────────────────────────────────────────────────┤
│                   EXTERNAL API                          │
│  (Red Hat Quay API)                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Verzeichnisstruktur

```
src/
├── main.py                    # Einstiegspunkt
├── config/
│   ├── loader.py              # Lädt settings.yaml + Env-Vars
│   └── settings.yaml          # Standard-Konfiguration
├── engine/
│   ├── pipeline_engine.py     # Orchestrator (lädt Pipeline, führt aus)
│   ├── pipeline_executor.py   # Führt einzelne Steps aus
│   ├── pipeline_validator.py  # Prüft Jobs gegen Registry
│   └── action_registry.py     # Mappt Job-Namen → Action-Klassen
├── engine_reader/
│   └── pipeline_reader.py     # YAML-Parsing + Template-Auflösung
├── gateway/
│   ├── quay_gateway.py        # Quay API Abstraktionsschicht
│   └── client.py              # HTTP-Client (Auth, TLS, Fehler)
├── actions/                   # 8 Action-Klassen
│   ├── create_organization.py
│   ├── delete_organization.py
│   ├── get_organization.py
│   ├── list_organizations.py
│   ├── create_robot_account.py
│   ├── delete_robot_account.py
│   ├── get_robot_account.py
│   └── list_robot_accounts.py
├── model/                     # Pydantic-Modelle
│   ├── pipeline_model.py      # PipelineStep, PipelineDefinition
│   ├── action_response.py     # ActionResponse
│   ├── organization_model.py
│   └── robot_account_model.py
├── pipelines/
│   ├── pipeline.yaml          # Pipeline-Definition
│   └── inputs.yaml            # Eingabedaten
└── utils/
    └── logger.py              # Farbiges Logging
```

---

## Wichtige Dateien & Codelocations

| Datei | Zeilen | Beschreibung |
|-------|--------|--------------|
| `src/main.py` | ~50 | Entry Point, lädt Config, startet Engine |
| `src/engine/pipeline_engine.py` | ~100 | Hauptorchestrierung |
| `src/engine/pipeline_executor.py` | ~150 | Step-Ausführung mit dynamischen Params |
| `src/engine/action_registry.py` | ~20 | ACTION_REGISTRY Dictionary |
| `src/gateway/quay_gateway.py` | ~100 | Alle Quay API Calls |
| `src/gateway/client.py` | ~200 | HTTP-Client mit Auth & Error-Handling |
| `src/config/loader.py` | ~80 | Config-Loading (YAML + Env) |

---

## ACTION_REGISTRY

```python
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
```

---

## Pipeline-Syntax

### pipeline.yaml
```yaml
pipeline:
  - name: create-organizations
    job: create_organization          # Muss in ACTION_REGISTRY existieren
    enabled: true
    params_list: "{{ organizations }}" # Dynamisch aus inputs.yaml

  - name: create-robot-accounts
    job: create_robot_account
    enabled: true
    params_list: "{{ robot_accounts }}"
```

### inputs.yaml
```yaml
organizations:
  - name: "testhome"
    visibility: "private"
    email: "test@test.ch"

robot_accounts:
  - organization: "testhome"
    robot_shortname: "ci-bot"
    description: "CI automation bot"
```

### Template-Auflösung
- `{{ organizations }}` → Liste aus inputs.yaml
- Jedes Item wird einzeln an die Action übergeben
- Statische Params: `params: {key: value}` statt `params_list`

---

## Konfiguration

### settings.yaml
```yaml
api:
  host: "http://127.0.0.1"
  port: 9080
  base_path: "/api/v1"
auth:
  token: "xxx"
  type: "bearer"   # bearer | basic | apikey
debug:
  enabled: true
app:
  version: "2.2.3"
```

### Environment Variables (überschreiben settings.yaml)
```
API_HOST, API_PORT, API_BASE_PATH
API_AUTH_TYPE, API_TOKEN
DISABLE_TLS_VERIFY
```

---

## Response-Muster

Alle Actions geben `ActionResponse` zurück:
```python
ActionResponse(
    success: bool,      # False → Pipeline stoppt
    message: str,       # Fehlerbeschreibung
    data: Any           # Zusätzliche Daten
)
```

---

## Besonderheiten der Quay API

1. **Robot Pre-Check:** GET auf Robot gibt 400 zurück wenn nicht existent (nicht 404)
2. **"Existing robot" Exception:** Wird abgefangen und als Erfolg behandelt
3. **Redirects:** 301/308 werden manuell behandelt

---

## Ausführungsablauf

```
1. main.py startet
2. Config laden (settings.yaml + Env)
3. PipelineEngine erstellen
4. Pipeline YAML laden
5. Templates auflösen ({{ key }} → Werte aus inputs)
6. Pipeline validieren (Jobs in Registry?)
7. Für jeden Step:
   - Action aus Registry holen
   - Bei params_list: Für jedes Item execute()
   - Bei params: Einmal execute()
   - Bei success=False: Pipeline abbrechen
8. Ausführungszeit loggen
```

---

## Deployment

### Docker
```bash
docker build -t quay-provisioner .
docker-compose up
```

### Kubernetes/Helm
```bash
helm install quay-provisioner ./helm \
  --set secrets.apiToken=xxx \
  --set secrets.apiHost=quay.example.com
```

Helm-Dateien in `helm/`:
- `job.yaml` - Kubernetes Job
- `pipeline-config.yaml` - ConfigMap für Pipelines
- `quay-config-secret.yaml` - Secret für Credentials

---

## Logging

Farbcodiert:
- **Blau:** DEBUG
- **Grün:** INFO
- **Rot:** ERROR

Debug aktivieren in `settings.yaml`:
```yaml
debug:
  enabled: true
```

---

## Neue Action hinzufügen

1. Pydantic-Modell in `src/model/` erstellen
2. Action-Klasse in `src/actions/` erstellen:
   ```python
   class NewAction:
       def __init__(self, gateway=None):
           self.gateway = gateway or QuayGateway()

       def execute(self, data: dict) -> ActionResponse:
           # Validierung mit Pydantic
           # Gateway-Aufruf
           # ActionResponse zurückgeben
   ```
3. Gateway-Methode in `src/gateway/quay_gateway.py` hinzufügen
4. In `src/engine/action_registry.py` registrieren:
   ```python
   ACTION_REGISTRY["new_action"] = NewAction
   ```

---

## Dependencies

```
pydantic          # Datenvalidierung
requests          # HTTP-Client
PyYAML==6.0.1     # YAML-Parsing
```

---

## Letzte Änderungen (Git Log)

- Verbessertes dynamisches Parameter-Handling
- Erweitertes Debug-Logging
- Bessere Fehlerbehandlung und Validierung
- App-Version in Konfiguration

---

*Erstellt: 2026-01-08*
