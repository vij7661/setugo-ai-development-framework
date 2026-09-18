#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$RUNTIME_DIR/.gate-build"
SRC="$RUNTIME_DIR/native/v24_v6_external_authority_gate.c"
WORKER="$RUNTIME_DIR/v24_v6_external_gate_worker.py"
PRC="$RUNTIME_DIR/v24_v6_proof_reference_closure.py"
ROOT_ATTEST="$RUNTIME_DIR/v24_v6_root_attestation.py"
FOUNDATION="$RUNTIME_DIR/v24_v6_governance_foundation.py"
DECISION_APPLY="$RUNTIME_DIR/v24_v6_decision_apply.py"
MATERIAL_SURFACE="$RUNTIME_DIR/v24_v6_material_surface.py"
NORMATIVE_PROJECTION="$RUNTIME_DIR/v24_v6_normative_clause_projection.py"
NORMATIVE_CATALOG="$RUNTIME_DIR/normative_control_catalog.py"
OUT="$BUILD_DIR/v24_v6_external_authority_gate"

mkdir -p "$BUILD_DIR"

sha_file() {
  sha256sum "$1" | awk '{print $1}'
}

SRC_SHA="$(sha_file "$SRC")"
WORKER_SHA="$(sha_file "$WORKER")"
PRC_SHA="$(sha_file "$PRC")"
ROOT_SHA="$(sha_file "$ROOT_ATTEST")"
FOUNDATION_SHA="$(sha_file "$FOUNDATION")"
DECISION_APPLY_SHA="$(sha_file "$DECISION_APPLY")"
MATERIAL_SURFACE_SHA="$(sha_file "$MATERIAL_SURFACE")"
NORMATIVE_PROJECTION_SHA="$(sha_file "$NORMATIVE_PROJECTION")"
NORMATIVE_CATALOG_SHA="$(sha_file "$NORMATIVE_CATALOG")"
BUILD_SCRIPT_SHA="$(sha_file "${BASH_SOURCE[0]}")"

BUILD_INPUT_SHA="$(
  printf '%s\n' \
    "schema=V24_V6_EXTERNAL_AUTHORITY_GATE_BUILD_V1" \
    "gate_source=$SRC_SHA" \
    "worker=$WORKER_SHA" \
    "proof_reference_closure=$PRC_SHA" \
    "root_attestation=$ROOT_SHA" \
    "governance_foundation=$FOUNDATION_SHA" \
    "decision_apply=$DECISION_APPLY_SHA" \
    "material_surface=$MATERIAL_SURFACE_SHA" \
    "normative_clause_projection=$NORMATIVE_PROJECTION_SHA" \
    "normative_control_catalog=$NORMATIVE_CATALOG_SHA" \
    "build_script=$BUILD_SCRIPT_SHA" \
  | sha256sum | awk '{print $1}'
)"

gcc \
  -std=c11 \
  -O2 \
  -Wall \
  -Wextra \
  -Wno-deprecated-declarations \
  -DEXPECTED_WORKER_SHA256="\"$WORKER_SHA\"" \
  -DEXPECTED_PRC_SHA256="\"$PRC_SHA\"" \
  -DEXPECTED_ROOT_SHA256="\"$ROOT_SHA\"" \
  -DEXPECTED_FOUNDATION_SHA256="\"$FOUNDATION_SHA\"" \
  -DEXPECTED_DECISION_APPLY_SHA256="\"$DECISION_APPLY_SHA\"" \
  -DEXPECTED_MATERIAL_SURFACE_SHA256="\"$MATERIAL_SURFACE_SHA\"" \
  -DEXPECTED_NORMATIVE_PROJECTION_SHA256="\"$NORMATIVE_PROJECTION_SHA\"" \
  -DEXPECTED_NORMATIVE_CATALOG_SHA256="\"$NORMATIVE_CATALOG_SHA\"" \
  -DBUILD_INPUT_SHA256="\"$BUILD_INPUT_SHA\"" \
  "$SRC" \
  -o "$OUT" \
  -lcrypto

chmod 0555 "$OUT"

BINARY_SHA="$(sha_file "$OUT")"
cat > "$BUILD_DIR/v24_v6_external_authority_gate_build.json" <<EOF
{
  "schema_version": 1,
  "gate_id": "V24-V6-EXTERNAL-AUTHORITY-GATE",
  "gate_version": "1",
  "build_input_sha256": "$BUILD_INPUT_SHA",
  "binary_sha256": "$BINARY_SHA",
  "gate_source_sha256": "$SRC_SHA",
  "worker_sha256": "$WORKER_SHA",
  "proof_reference_closure_sha256": "$PRC_SHA",
  "root_attestation_sha256": "$ROOT_SHA",
  "governance_foundation_sha256": "$FOUNDATION_SHA",
  "decision_apply_sha256": "$DECISION_APPLY_SHA",
  "material_surface_sha256": "$MATERIAL_SURFACE_SHA",
  "normative_clause_projection_sha256": "$NORMATIVE_PROJECTION_SHA",
  "normative_control_catalog_sha256": "$NORMATIVE_CATALOG_SHA",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_state": "NOT_CLAIMED"
}
EOF

"$OUT" --identity
cat "$BUILD_DIR/v24_v6_external_authority_gate_build.json"
