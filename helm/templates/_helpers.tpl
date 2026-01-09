{{/*
Expand the name of the chart.
*/}}
{{- define "quay-provisioner.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "quay-provisioner.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "quay-provisioner.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "quay-provisioner.labels" -}}
helm.sh/chart: {{ include "quay-provisioner.chart" . }}
{{ include "quay-provisioner.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "quay-provisioner.selectorLabels" -}}
app.kubernetes.io/name: {{ include "quay-provisioner.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "quay-provisioner.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "quay-provisioner.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "quay-provisioner.secretName" -}}
{{- if .Values.secrets.existingSecret }}
{{- .Values.secrets.existingSecret }}
{{- else }}
{{- default (printf "%s-config" (include "quay-provisioner.fullname" .)) .Values.secrets.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the configmap for pipelines
*/}}
{{- define "quay-provisioner.pipelinesConfigMapName" -}}
{{- default (printf "%s-pipelines" (include "quay-provisioner.fullname" .)) .Values.pipelines.configMapName }}
{{- end }}