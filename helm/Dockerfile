FROM amazonlinux:2

LABEL maintainer="Accern DevOps <devops@accern.com>"

# Install helm
# https://helm.sh/docs/intro/install/#from-the-binary-releases
RUN yum -y update && \
    yum install -y wget tar gzip && \
    wget https://get.helm.sh/helm-v3.8.0-linux-amd64.tar.gz -O helm.tar.gz && \
    tar -xvzf helm.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/helm && \
    helm version

# https://helm.sh/docs/intro/install/#from-script
# RUN yum -y update && \
#     yum install -y tar gzip openssl && \
#     curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && \
#     chmod 700 get_helm.sh && \
#     ./get_helm.sh && \
#     helm version

# Install helm cm-push plugin
# https://github.com/chartmuseum/helm-push#install
RUN yum install -y git && \
    helm plugin install https://github.com/chartmuseum/helm-push.git && \
    helm cm-push --help
