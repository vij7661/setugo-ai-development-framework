#!/usr/bin/env bash
set -euo pipefail

EXPECTED_MANIFEST_SHA256="42e24fc1f7fac57966fcfdf67c06c68e0ffb9c4b102ddb487559fc4f2bb66e03"
TRUSTED_ROOT="/opt/v24-v6-trusted-runtime"
EXPECTED_SOCKET="/run/v24-v6-authority/service.sock"
EXPECTED_CANDIDATE="v24candidate"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Successor-7 trusted bootstrap requires root" >&2
  exit 2
fi

if [[ -n "${V24_V6_TRUSTED_ROOT+x}" ]]; then
  echo "candidate-selected trusted root is forbidden" >&2
  exit 3
fi

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 <candidate-runtime-dir> <external-bootstrap-manifest>" >&2
  exit 2
fi

SRC="$(realpath -e "$1")"
MANIFEST="$(realpath -e "$2")"

test -d "$SRC"
test -f "$MANIFEST"

actual_manifest_sha="$(sha256sum "$MANIFEST" | awk '{print $1}')"
test "$actual_manifest_sha" = "$EXPECTED_MANIFEST_SHA256"

test "$(jq -r '.manifest_id' "$MANIFEST")" = "V24-V6-SUCCESSOR7-TRUSTED-SERVICE-BOOTSTRAP-V1"
test "$(jq -r '.service_id' "$MANIFEST")" = "V24-V6-TRUSTED-AUTHORITY-SERVICE"
test "$(jq -r '.service_version' "$MANIFEST")" = "1"
test "$(jq -r '.gate_id' "$MANIFEST")" = "V24-V6-EXTERNAL-AUTHORITY-GATE"
test "$(jq -r '.gate_version' "$MANIFEST")" = "1"
test "$(jq -r '.trusted_root' "$MANIFEST")" = "$TRUSTED_ROOT"
test "$(jq -r '.trusted_socket_path' "$MANIFEST")" = "$EXPECTED_SOCKET"
test "$(jq -r '.candidate_identity' "$MANIFEST")" = "$EXPECTED_CANDIDATE"
test "$(jq -r '.authority_effect' "$MANIFEST")" = "NONE_EVIDENCE_ONLY"
test "$(jq -r '.runtime_qualification_state' "$MANIFEST")" = "NOT_CLAIMED"

if ! id "$EXPECTED_CANDIDATE" >/dev/null 2>&1; then
  echo "fixed candidate identity missing" >&2
  exit 4
fi
test "$(id -u "$EXPECTED_CANDIDATE")" != "0"

STAGE="$(mktemp -d /var/tmp/v24-v6-s7-bootstrap.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
install -d -o root -g root -m 0700 "$STAGE"

mapfile -t FILES < <(jq -r '.files | keys[]' "$MANIFEST")
for rel in "${FILES[@]}"; do
  src="$SRC/$rel"
  dst="$STAGE/$rel"
  test -f "$src"
  install -D -o root -g root -m 0444 "$src" "$dst"
  expected="$(jq -r --arg p "$rel" '.files[$p]' "$MANIFEST")"
  actual="$(sha256sum "$dst" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    echo "external bootstrap source digest mismatch: $rel" >&2
    exit 5
  fi
done

chmod 0555 "$STAGE/build_v24_v6_external_authority_gate.sh"
chmod 0555 "$STAGE/build_v24_v6_trusted_authority_service.sh"

env -i PATH=/usr/bin:/bin LC_ALL=C.UTF-8 \
  bash "$STAGE/build_v24_v6_external_authority_gate.sh" >/tmp/v24-s7-gate-build.log
env -i PATH=/usr/bin:/bin LC_ALL=C.UTF-8 \
  bash "$STAGE/build_v24_v6_trusted_authority_service.sh" >/tmp/v24-s7-service-build.log

expected_gate="$(jq -r '.gate_binary_sha256' "$MANIFEST")"
expected_gate_build="$(jq -r '.gate_build_input_sha256' "$MANIFEST")"
actual_gate="$(sha256sum "$STAGE/.gate-build/v24_v6_external_authority_gate" | awk '{print $1}')"
actual_gate_build="$(jq -r '.build_input_sha256' "$STAGE/.gate-build/v24_v6_external_authority_gate_build.json")"
test "$actual_gate" = "$expected_gate"
test "$actual_gate_build" = "$expected_gate_build"

expected_service="$(jq -r '.service_binary_sha256' "$MANIFEST")"
expected_service_build="$(jq -r '.service_build_input_sha256' "$MANIFEST")"
actual_service="$(sha256sum "$STAGE/.service-build/v24_v6_trusted_authority_service" | awk '{print $1}')"
actual_service_build="$(jq -r '.build_input_sha256' "$STAGE/.service-build/v24_v6_trusted_authority_service_build.json")"
test "$actual_service" = "$expected_service"
test "$actual_service_build" = "$expected_service_build"

rm -rf "$TRUSTED_ROOT"
install -d -o root -g root -m 0755 "$TRUSTED_ROOT"
install -d -o root -g root -m 0755 "$TRUSTED_ROOT/.gate-build"
install -d -o root -g root -m 0755 "$TRUSTED_ROOT/bootstrap"

PYFILES=(
  v24_v6_external_gate_worker.py
  v24_v6_proof_reference_closure.py
  v24_v6_root_attestation.py
  v24_v6_governance_foundation.py
  v24_v6_decision_apply.py
  v24_v6_material_surface.py
  v24_v6_normative_clause_projection.py
  normative_control_catalog.py
)

for name in "${PYFILES[@]}"; do
  install -o root -g root -m 0444 "$STAGE/$name" "$TRUSTED_ROOT/$name"
done

install -o root -g root -m 0555 \
  "$STAGE/.gate-build/v24_v6_external_authority_gate" \
  "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate"
install -o root -g root -m 0444 \
  "$STAGE/.gate-build/v24_v6_external_authority_gate_build.json" \
  "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate_build.json"
install -o root -g root -m 0555 \
  "$STAGE/.service-build/v24_v6_trusted_authority_service" \
  "$TRUSTED_ROOT/v24_v6_trusted_authority_service"
install -o root -g root -m 0444 \
  "$STAGE/.service-build/v24_v6_trusted_authority_service_build.json" \
  "$TRUSTED_ROOT/v24_v6_trusted_authority_service_build.json"
install -o root -g root -m 0444 "$MANIFEST" \
  "$TRUSTED_ROOT/bootstrap/v24-v6-successor7-trusted-service-bootstrap-v1.json"

chown -R root:root "$TRUSTED_ROOT"
find "$TRUSTED_ROOT" -type f -name '*.py' -exec chmod 0444 {} +
chmod 0555 "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate"
chmod 0444 "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate_build.json"
chmod 0555 "$TRUSTED_ROOT/v24_v6_trusted_authority_service"
chmod 0444 "$TRUSTED_ROOT/v24_v6_trusted_authority_service_build.json"
chmod 0444 "$TRUSTED_ROOT/bootstrap/v24-v6-successor7-trusted-service-bootstrap-v1.json"
chmod 0555 "$TRUSTED_ROOT/.gate-build"
chmod 0555 "$TRUSTED_ROOT/bootstrap"
chmod 0555 "$TRUSTED_ROOT"

test "$(sha256sum "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate" | awk '{print $1}')" = "$expected_gate"
test "$(sha256sum "$TRUSTED_ROOT/v24_v6_trusted_authority_service" | awk '{print $1}')" = "$expected_service"
test "$(sha256sum "$TRUSTED_ROOT/bootstrap/v24-v6-successor7-trusted-service-bootstrap-v1.json" | awk '{print $1}')" = "$EXPECTED_MANIFEST_SHA256"

"$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate" --identity
"$TRUSTED_ROOT/v24_v6_trusted_authority_service" --identity
