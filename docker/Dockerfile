# =============================================================================
# Multi-stage production Dockerfile for AICreator
# Contains: Python 3.12, Go 1.23, buf 1.50.0, protoc 29.3,
#           openapi-generator 7.12.0, JRE 21, golangci-lint 1.63.4,
#           protoc-gen-go, protoc-gen-go-grpc
# =============================================================================

# Stage 1: Go toolchain — install Go tools (protoc-gen-go, golangci-lint)
FROM golang:1.23-alpine AS go-tools

RUN apk add --no-cache git

# Install protoc-gen-go and protoc-gen-go-grpc
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.6 && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1

# Install golangci-lint
RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.63.4

# Stage 2: Download buf and protoc binaries
FROM alpine:3.21 AS binaries

RUN apk add --no-cache curl unzip

# Download buf v1.50.0
RUN curl -sSL "https://github.com/bufbuild/buf/releases/download/v1.50.0/buf-Linux-x86_64" \
    -o /usr/local/bin/buf && \
    chmod +x /usr/local/bin/buf

# Download protoc v29.3
RUN curl -sSL "https://github.com/protocolbuffers/protobuf/releases/download/v29.3/protoc-29.3-linux-x86_64.zip" \
    -o /tmp/protoc.zip && \
    unzip /tmp/protoc.zip -d /opt/protoc && \
    rm /tmp/protoc.zip

# Stage 3: Runtime — Python 3.12 + all tools
FROM python:3.12-slim AS runtime

# Install system dependencies: JRE for openapi-generator, Go runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-21-jre-headless \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Go 1.23 runtime (needed for postprocessor: gofmt, go build)
COPY --from=golang:1.23-alpine /usr/local/go /usr/local/go
ENV GOROOT=/usr/local/go
ENV GOPATH=/go
ENV PATH="/usr/local/go/bin:/go/bin:${PATH}"

# Copy Go tools from Stage 1
COPY --from=go-tools /go/bin/protoc-gen-go /go/bin/
COPY --from=go-tools /go/bin/protoc-gen-go-grpc /go/bin/
COPY --from=go-tools /go/bin/golangci-lint /go/bin/

# Copy buf and protoc from Stage 2
COPY --from=binaries /usr/local/bin/buf /usr/local/bin/buf
COPY --from=binaries /opt/protoc/bin/protoc /usr/local/bin/protoc
COPY --from=binaries /opt/protoc/include/ /usr/local/include/

# Download openapi-generator JAR v7.12.0
RUN mkdir -p /opt/openapi-generator && \
    curl -sSL "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.12.0/openapi-generator-cli-7.12.0.jar" \
    -o /opt/openapi-generator/openapi-generator-cli.jar

# Install uv for Python dependency management
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies (no dev deps)
RUN uv sync --no-dev --frozen

# Copy application code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini ./

# Copy entrypoint
COPY docker/entrypoint.prod.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Verify tools are installed
RUN go version && \
    buf --version && \
    protoc --version && \
    golangci-lint --version && \
    java -jar /opt/openapi-generator/openapi-generator-cli.jar version && \
    uv run python -c "from aicreator import __version__; print(f'aicreator {__version__}')"

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
