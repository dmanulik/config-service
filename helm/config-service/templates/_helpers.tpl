{{/*
Expand the name of the chart.
*/}}
{{- define "config-service.name" -}}
{{- default .Chart.Name .Values.configservice.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "config-service.fullname" -}}
{{- if .Values.configservice.fullnameOverride }}
{{- .Values.configservice.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.configservice.nameOverride }}
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
{{- define "config-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "config-service.labels" -}}
helm.sh/chart: {{ include "config-service.chart" . }}
{{ include "config-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "config-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "config-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "config-service.serviceAccountName" -}}
{{- if .Values.configservice.serviceAccount.create }}
{{- default (include "config-service.fullname" .) .Values.configservice.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.configservice.serviceAccount.name }}
{{- end }}
{{- end }}
