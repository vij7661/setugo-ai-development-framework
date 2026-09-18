#!/usr/bin/env bash
set -euo pipefail

EXPECTED_MANIFEST_BLOB_SHA1="8fe0ad1c96d1f1c2ce855846dfe342c79d947483"
TRUSTED_ROOT="/opt/v24-v6-trusted-runtime"
EXPECTED_SOCKET="/run/v24-v6-authority/service.sock"
EXPECTED_CANDIDATE="v24candidate"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Successor-8 trusted bootstrap requires root" >&2
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

command -v git >/dev/null
command -v jq >/dev/null
command -v sha256sum >/dev/null
command -v gcc >/dev/null

SRC="$(realpath -e "$1")"
MANIFEST="$(realpath -e "$2")"
test -d "$SRC"
test -f "$MANIFEST"

actual_manifest_blob="$(git hash-object "$MANIFEST")"
test "$actual_manifest_blob" = "$EXPECTED_MANIFEST_BLOB_SHA1"

test "$(jq -r '.schema_version' "$MANIFEST")" = "4"
test "$(jq -r '.file_hash_mode' "$MANIFEST")" = "git_blob_sha1"
test "$(jq -r '.manifest_id' "$MANIFEST")" = "V24-V6-SUCCESSOR8-TRUSTED-AUTHORITY-BOOTSTRAP-V4"
test "$(jq -r '.service_id' "$MANIFEST")" = "V24-V6-TRUSTED-AUTHORITY-SERVICE"
test "$(jq -r '.service_version' "$MANIFEST")" = "2"
test "$(jq -r '.gate_id' "$MANIFEST")" = "V24-V6-EXTERNAL-AUTHORITY-GATE"
test "$(jq -r '.gate_version' "$MANIFEST")" = "1"
test "$(jq -r '.trusted_root' "$MANIFEST")" = "$TRUSTED_ROOT"
test "$(jq -r '.trusted_socket_path' "$MANIFEST")" = "$EXPECTED_SOCKET"
test "$(jq -r '.candidate_identity' "$MANIFEST")" = "$EXPECTED_CANDIDATE"
test "$(jq -r '.authority_effect' "$MANIFEST")" = "NONE_EVIDENCE_ONLY"
test "$(jq -r '.runtime_qualification_state' "$MANIFEST")" = "NOT_CLAIMED"
test "$(jq -r '.authority_record_schema' "$MANIFEST")" = "V24_V6_S8_AUTHORITY_RECORD_V1"
test "$(jq -r '.consumption_mode' "$MANIFEST")" = "ROOT_ONLY_ONE_SHOT"
test "$(jq -r '.record_pending_dir' "$MANIFEST")" = "/run/v24-v6-authority/private/records"
test "$(jq -r '.record_consumed_dir' "$MANIFEST")" = "/run/v24-v6-authority/private/consumed"

if ! id "$EXPECTED_CANDIDATE" >/dev/null 2>&1; then
  echo "fixed candidate identity missing" >&2
  exit 4
fi
test "$(id -u "$EXPECTED_CANDIDATE")" != "0"

STAGE="$(mktemp -d /var/tmp/v24-v6-s8-bootstrap.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
chmod 0700 "$STAGE"

mapfile -t FILES < <(jq -r '.files | keys[]' "$MANIFEST")
for rel in "${FILES[@]}"; do
  src="$SRC/$rel"
  dst="$STAGE/$rel"
  test -f "$src"
  install -D -o root -g root -m 0444 "$src" "$dst"
  expected="$(jq -r --arg p "$rel" '.files[$p]' "$MANIFEST")"
  actual="$(git hash-object "$dst")"
  if [[ "$actual" != "$expected" ]]; then
    echo "external bootstrap source blob mismatch: $rel" >&2
    exit 5
  fi
done

chmod 0555 "$STAGE/build_v24_v6_external_authority_gate.sh"
chmod 0555 "$STAGE/build_v24_v6_trusted_authority_service.sh"

env -i PATH=/usr/bin:/bin LC_ALL=C.UTF-8   bash "$STAGE/build_v24_v6_external_authority_gate.sh" >/var/tmp/v24-s8-gate-build.log
env -i PATH=/usr/bin:/bin LC_ALL=C.UTF-8   bash "$STAGE/build_v24_v6_trusted_authority_service.sh" >/var/tmp/v24-s8-service-build.log

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

install -o root -g root -m 0555   "$STAGE/.gate-build/v24_v6_external_authority_gate"   "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate"
install -o root -g root -m 0444   "$STAGE/.gate-build/v24_v6_external_authority_gate_build.json"   "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate_build.json"
install -o root -g root -m 0555   "$STAGE/.service-build/v24_v6_trusted_authority_service"   "$TRUSTED_ROOT/v24_v6_trusted_authority_service"
install -o root -g root -m 0444   "$STAGE/.service-build/v24_v6_trusted_authority_service_build.json"   "$TRUSTED_ROOT/v24_v6_trusted_authority_service_build.json"
install -o root -g root -m 0444 "$MANIFEST"   "$TRUSTED_ROOT/bootstrap/v24-v6-successor8-trusted-authority-bootstrap-v4.json"

chown -R root:root "$TRUSTED_ROOT"
find "$TRUSTED_ROOT" -type f -name '*.py' -exec chmod 0444 {} +
chmod 0555 "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate"
chmod 0444 "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate_build.json"
chmod 0555 "$TRUSTED_ROOT/v24_v6_trusted_authority_service"
chmod 0444 "$TRUSTED_ROOT/v24_v6_trusted_authority_service_build.json"
chmod 0444 "$TRUSTED_ROOT/bootstrap/v24-v6-successor8-trusted-authority-bootstrap-v4.json"
chmod 0555 "$TRUSTED_ROOT/.gate-build"
chmod 0555 "$TRUSTED_ROOT/bootstrap"
chmod 0555 "$TRUSTED_ROOT"

test "$(sha256sum "$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate" | awk '{print $1}')" = "$expected_gate"
test "$(sha256sum "$TRUSTED_ROOT/v24_v6_trusted_authority_service" | awk '{print $1}')" = "$expected_service"
test "$(git hash-object "$TRUSTED_ROOT/bootstrap/v24-v6-successor8-trusted-authority-bootstrap-v4.json")" = "$EXPECTED_MANIFEST_BLOB_SHA1"

"$TRUSTED_ROOT/.gate-build/v24_v6_external_authority_gate" --identity
"$TRUSTED_ROOT/v24_v6_trusted_authority_service" --identity
