#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$RUNTIME_DIR/.service-build"
SRC="$RUNTIME_DIR/native/v24_v6_trusted_authority_service.c"
OUT="$BUILD_DIR/v24_v6_trusted_authority_service"

mkdir -p "$BUILD_DIR"

sha_file() {
  sha256sum "$1" | awk '{print $1}'
}

SRC_SHA="$(sha_file "$SRC")"
BUILD_SCRIPT_SHA="$(sha_file "${BASH_SOURCE[0]}")"
BUILD_INPUT_SHA="$(
  printf '%s\n' \
    "schema=V24_V6_TRUSTED_AUTHORITY_SERVICE_BUILD_V1" \
    "service_source=$SRC_SHA" \
    "build_script=$BUILD_SCRIPT_SHA" \
  | sha256sum | awk '{print $1}'
)"

gcc \
  -std=c11 \
  -O2 \
  -Wall \
  -Wextra \
  -Werror \
  -DBUILD_INPUT_SHA256="\\\"$BUILD_INPUT_SHA\\\"" \
  "$SRC" \
  -o "$OUT" \
  -lcrypto

chmod 0555 "$OUT"
BINARY_SHA="$(sha_file "$OUT")"

cat > "$BUILD_DIR/v24_v6_trusted_authority_service_build.json" <<EOF
{
  "schema_version": 1,
  "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE",
  "service_version": "2",
  "build_input_sha256": "$BUILD_INPUT_SHA",
  "binary_sha256": "$BINARY_SHA",
  "service_source_sha256": "$SRC_SHA",
  "build_script_sha256": "$BUILD_SCRIPT_SHA",
  "trusted_socket_path": "/run/v24-v6-authority/service.sock",
  "trusted_root": "/opt/v24-v6-trusted-runtime",
  "candidate_identity": "v24candidate",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_state": "NOT_CLAIMED"
}
EOF

"$OUT" --identity
cat "$BUILD_DIR/v24_v6_trusted_authority_service_build.json"
