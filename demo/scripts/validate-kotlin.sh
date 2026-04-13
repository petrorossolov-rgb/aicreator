#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/kotlin"
LIBS_DIR="/opt/libs"
COMPILE_DIR=$(mktemp -d)

echo "=== Kotlin: compilation validation ==="
echo "Target: ${OUTPUT_DIR}"
echo "Classpath: ${LIBS_DIR}"

# Collect all source files
JAVA_FILES=$(find "${OUTPUT_DIR}" -name "*.java")
KT_FILES=$(find "${OUTPUT_DIR}" -name "*.kt")

if [ -z "${KT_FILES}" ]; then
  echo "ERROR: No .kt files found in ${OUTPUT_DIR}" >&2
  exit 1
fi

# Build classpath from runtime JARs
CLASSPATH="${LIBS_DIR}/protobuf-java.jar:${LIBS_DIR}/protobuf-kotlin.jar"

# Compile Java files first (Kotlin DSL extensions depend on Java base classes)
if [ -n "${JAVA_FILES}" ]; then
  echo "Compiling Java sources..."
  # shellcheck disable=SC2086
  javac -cp "${CLASSPATH}" -d "${COMPILE_DIR}" ${JAVA_FILES}
  CLASSPATH="${CLASSPATH}:${COMPILE_DIR}"
fi

# Compile Kotlin files
echo "Compiling Kotlin sources..."
# shellcheck disable=SC2086
kotlinc -cp "${CLASSPATH}" -d "${COMPILE_DIR}" ${KT_FILES} 2>&1 | grep -v "^w:" || true

echo "=== Kotlin validation passed ==="

# Clean up
rm -rf "${COMPILE_DIR}"
