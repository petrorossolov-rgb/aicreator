FROM golang:1.23-alpine

# Install system dependencies (JRE for openapi-generator-cli)
RUN apk add --no-cache curl bash openjdk17-jre-headless

# Download openapi-generator-cli JAR
ARG OPENAPI_GENERATOR_VERSION=7.12.0
RUN mkdir -p /opt/openapi-generator && \
    curl -sSL "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/${OPENAPI_GENERATOR_VERSION}/openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar" \
      -o /opt/openapi-generator/openapi-generator-cli.jar

# Install golangci-lint
ARG GOLANGCI_LINT_VERSION=1.63.4
RUN curl -sSL "https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh" | \
    sh -s -- -b /usr/local/bin v${GOLANGCI_LINT_VERSION}

WORKDIR /workspace

ENTRYPOINT ["/bin/bash"]
