#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "trusted gate installation requires root" >&2
  exit 2
fi

SRC_RUNTIME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${V24_V6_TRUSTED_ROOT:-/opt/v24-v6-trusted-runtime}"
BUILD_DIR="$SRC_RUNTIME/.gate-build"
GATE="$BUILD_DIR/v24_v6_external_authority_gate"
BUILD_JSON="$BUILD_DIR/v24_v6_external_authority_gate_build.json"

test -x "$GATE"
test -f "$BUILD_JSON"

FILES=(
  v24_v6_external_gate_worker.py
  v24_v6_proof_reference_closure.py
  v24_v6_root_attestation.py
  v24_v6_governance_foundation.py
  v24_v6_decision_apply.py
  v24_v6_material_surface.py
  v24_v6_normative_clause_projection.py
  normative_control_catalog.py
)

rm -rf "$DEST"
install -d -o root -g root -m 0755 "$DEST"
install -d -o root -g root -m 0755 "$DEST/.gate-build"

for name in "${FILES[@]}"; do
  install -o root -g root -m 0444 "$SRC_RUNTIME/$name" "$DEST/$name"
done

install -o root -g root -m 0555 "$GATE" "$DEST/.gate-build/v24_v6_external_authority_gate"
install -o root -g root -m 0444 "$BUILD_JSON" "$DEST/.gate-build/v24_v6_external_authority_gate_build.json"

expected_binary="$(jq -r '.binary_sha256' "$BUILD_JSON")"
actual_binary="$(sha256sum "$DEST/.gate-build/v24_v6_external_authority_gate" | awk '{print $1}')"
test "$actual_binary" = "$expected_binary"

declare -A EXPECTED=(
  [v24_v6_external_gate_worker.py]="$(jq -r '.worker_sha256' "$BUILD_JSON")"
  [v24_v6_proof_reference_closure.py]="$(jq -r '.proof_reference_closure_sha256' "$BUILD_JSON")"
  [v24_v6_root_attestation.py]="$(jq -r '.root_attestation_sha256' "$BUILD_JSON")"
  [v24_v6_governance_foundation.py]="$(jq -r '.governance_foundation_sha256' "$BUILD_JSON")"
  [v24_v6_decision_apply.py]="$(jq -r '.decision_apply_sha256' "$BUILD_JSON")"
  [v24_v6_material_surface.py]="$(jq -r '.material_surface_sha256' "$BUILD_JSON")"
  [v24_v6_normative_clause_projection.py]="$(jq -r '.normative_clause_projection_sha256' "$BUILD_JSON")"
  [normative_control_catalog.py]="$(jq -r '.normative_control_catalog_sha256' "$BUILD_JSON")"
)

for name in "${FILES[@]}"; do
  actual="$(sha256sum "$DEST/$name" | awk '{print $1}')"
  test "$actual" = "${EXPECTED[$name]}"
done

chown -R root:root "$DEST"
find "$DEST" -type f -name '*.py' -exec chmod 0444 {} +
chmod 0444 "$DEST/.gate-build/v24_v6_external_authority_gate_build.json"
chmod 0555 "$DEST/.gate-build/v24_v6_external_authority_gate"
chmod 0555 "$DEST/.gate-build"
chmod 0555 "$DEST"

"$DEST/.gate-build/v24_v6_external_authority_gate" --identity
