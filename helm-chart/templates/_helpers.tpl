{{- define "esConfig" }}
- name: DATA_{{ .type }}_HOST
  {{- if empty .servicePrefix }}
  value: {{ .host }}
  {{- else }}
  value: https://{{ .servicePrefix }}-es-http:9200
  {{- end }}
- name: DATA_{{ .type }}_HOST_PIPELINES
  value: {{ .extHost }}
- name: DATA_{{ .type }}_USER
  value: {{ .user | default "elastic" }}
- name: DATA_{{ .type }}_PASSWORD
  {{- if empty .servicePrefix }}
  value: {{ .password }}
  {{- else }}
  valueFrom:
    secretKeyRef:
        name: {{ .servicePrefix }}-es-elastic-user
        key: elastic
  {{- end}}
{{- end }}