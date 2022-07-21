# Updating the Helm chart

## Prepare
When updating the helm chart, similarly to a docker image, we need to publish the new version in order for it to be used by DevOps systems. 

To publish it you need to install:
- helm [https://helm.sh/]
- helm-push plugin [https://github.com/chartmuseum/helm-push/]

And add our chart-museum repository following instructions here: [https://myaccern.atlassian.net/l/c/Fv5H10wf]

## Publish the chart
Uocate then `version` field on the `Chart.yaml` file. 
Call `publish.sh` to publish the chart.

Comunicate DevOps about the new chart version. 