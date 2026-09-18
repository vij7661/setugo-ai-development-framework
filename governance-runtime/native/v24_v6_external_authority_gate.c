#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <openssl/bn.h>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/sha.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef EXPECTED_WORKER_SHA256
#define EXPECTED_WORKER_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_PRC_SHA256
#define EXPECTED_PRC_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_ROOT_SHA256
#define EXPECTED_ROOT_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_FOUNDATION_SHA256
#define EXPECTED_FOUNDATION_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_DECISION_APPLY_SHA256
#define EXPECTED_DECISION_APPLY_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_MATERIAL_SURFACE_SHA256
#define EXPECTED_MATERIAL_SURFACE_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_NORMATIVE_PROJECTION_SHA256
#define EXPECTED_NORMATIVE_PROJECTION_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_NORMATIVE_CATALOG_SHA256
#define EXPECTED_NORMATIVE_CATALOG_SHA256 "UNBUILT"
#endif
#ifndef BUILD_INPUT_SHA256
#define BUILD_INPUT_SHA256 "UNBUILT"
#endif

#define GATE_ID "V24-V6-EXTERNAL-AUTHORITY-GATE"
#define GATE_VERSION "1"
#define AUTHORITY_EFFECT "NONE_EVIDENCE_ONLY"

#define ATTESTATION_SCHEMA "1"
#define KEY_ID "V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V3"
#define ALGORITHM "RSA-PKCS1-v1_5-SHA256"
#define PURPOSE "V24_V6_CONSTRUCTION_PROOF_CONTEXT_ATTESTATION"
#define ATTESTATION_KEYS "algorithm,genesis_trusted_scope_digest,governance_generation_id,key_id,proof_context_digest,purpose,schema_version,signature_b64"
#define RSA_MODULUS_HEX "a859b1d6e482ee3a0b59cefea9a1506f27e2a76fb30b142bd2f224a3930ff4f904f765c3ad749dd81f7fa9a702f0a84cf29fdb25cefa8437c6403f72167195e4b87daa9f4dd2a3d25afd611f3732a3bbe1ab0225ed1922528e2b84fd141dea95f9feb07e901d94e6fb033af3f1a1c718c8c8952f8bf66a29723d3a7b8755e030dd5d29a87be2472a3fa3d2b51596092734a78113f4c6846790f02b6a9e2bce87abb69ebaf86fe2eb0d3de78c6f3dee723957f30593fc6bc4e7f41026ccb22d5271f3a391b355d5a62281f0193f33e5de96df50bbdfe554769cafe55b7a8f1e471ce47deb03bdbfafc37af2669570f89d1d512ebfb55c55e515dd9c69df9be65b"
#define RSA_EXPONENT 65537UL

#define MAX_CAPTURE (8U * 1024U * 1024U)

static void deny(const char *reason) {
    printf("{\"authority_effect\":\"%s\",\"construction_authoritative\":true,"
           "\"decision\":\"DENY\",\"gate_id\":\"%s\",\"gate_version\":\"%s\","
           "\"reason\":\"%s\"}\n",
           AUTHORITY_EFFECT, GATE_ID, GATE_VERSION, reason);
}

static bool is_hex64(const char *s) {
    if (!s || strlen(s) != 64) return false;
    for (size_t i = 0; i < 64; ++i) {
        char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

static unsigned char *read_file(const char *path, size_t *len_out) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long n = ftell(f);
    if (n < 0 || (unsigned long)n > MAX_CAPTURE) { fclose(f); return NULL; }
    if (fseek(f, 0, SEEK_SET) != 0) { fclose(f); return NULL; }
    unsigned char *buf = malloc((size_t)n + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t got = fread(buf, 1, (size_t)n, f);
    fclose(f);
    if (got != (size_t)n) { free(buf); return NULL; }
    buf[got] = '\0';
    *len_out = got;
    return buf;
}

static void sha256_hex_bytes(const unsigned char *data, size_t len, char out[65]) {
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(data, len, digest);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        sprintf(out + (i * 2), "%02x", digest[i]);
    }
    out[64] = '\0';
}

static bool sha256_file_matches(const char *path, const char *expected) {
    size_t len = 0;
    unsigned char *data = read_file(path, &len);
    if (!data) return false;
    char actual[65];
    sha256_hex_bytes(data, len, actual);
    free(data);
    return strcmp(actual, expected) == 0;
}

static char *capture_exec(char *const argv[], char *const envp[], int *status_out) {
    int pipefd[2];
    if (pipe(pipefd) != 0) return NULL;
    pid_t pid = fork();
    if (pid < 0) { close(pipefd[0]); close(pipefd[1]); return NULL; }
    if (pid == 0) {
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execve(argv[0], argv, envp);
        _exit(127);
    }
    close(pipefd[1]);
    size_t cap = 4096, len = 0;
    char *buf = malloc(cap);
    if (!buf) { close(pipefd[0]); return NULL; }
    while (1) {
        if (len + 2048 + 1 > cap) {
            size_t next = cap * 2;
            if (next > MAX_CAPTURE) { free(buf); close(pipefd[0]); return NULL; }
            char *tmp = realloc(buf, next);
            if (!tmp) { free(buf); close(pipefd[0]); return NULL; }
            buf = tmp; cap = next;
        }
        ssize_t n = read(pipefd[0], buf + len, cap - len - 1);
        if (n < 0) {
            if (errno == EINTR) continue;
            free(buf); close(pipefd[0]); return NULL;
        }
        if (n == 0) break;
        len += (size_t)n;
        if (len > MAX_CAPTURE) { free(buf); close(pipefd[0]); return NULL; }
    }
    close(pipefd[0]);
    int st = 0;
    if (waitpid(pid, &st, 0) < 0) { free(buf); return NULL; }
    buf[len] = '\0';
    while (len > 0 && (buf[len-1] == '\n' || buf[len-1] == '\r')) buf[--len] = '\0';
    if (status_out) *status_out = st;
    return buf;
}

static char *run_jq(const char *mode, const char *filter, const char *path, int *status_out) {
    char *const envp[] = { "PATH=/usr/bin:/bin", "LC_ALL=C.UTF-8", NULL };
    char *argv_raw[] = { "/usr/bin/jq", (char *)mode, (char *)filter, (char *)path, NULL };
    return capture_exec(argv_raw, envp, status_out);
}

static bool child_ok(int status) {
    return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

static int split_tsv(char *s, char **out, int max_fields) {
    int n = 0;
    char *p = s;
    if (max_fields <= 0) return 0;
    out[n++] = p;
    while (*p && n < max_fields) {
        if (*p == '\t') {
            *p = '\0';
            out[n++] = p + 1;
        }
        p++;
    }
    return n;
}

static bool b64_decode(const char *input, unsigned char **out, size_t *out_len) {
    if (!input) return false;
    size_t in_len = strlen(input);
    if (in_len == 0 || (in_len % 4) != 0) return false;
    size_t cap = (in_len / 4) * 3 + 3;
    unsigned char *buf = malloc(cap);
    if (!buf) return false;
    int n = EVP_DecodeBlock(buf, (const unsigned char *)input, (int)in_len);
    if (n < 0) { free(buf); return false; }
    size_t len = (size_t)n;
    if (in_len >= 1 && input[in_len-1] == '=') len--;
    if (in_len >= 2 && input[in_len-2] == '=') len--;
    *out = buf; *out_len = len;
    return true;
}

static bool verify_rsa_pkcs1_sha256(const unsigned char *message, size_t message_len, const char *sig_b64) {
    unsigned char *sig = NULL;
    size_t sig_len = 0;
    if (!b64_decode(sig_b64, &sig, &sig_len)) return false;

    BIGNUM *n = NULL, *e = NULL;
    RSA *rsa = RSA_new();
    if (!rsa) { free(sig); return false; }
    if (!BN_hex2bn(&n, RSA_MODULUS_HEX)) { RSA_free(rsa); free(sig); return false; }
    e = BN_new();
    if (!e || !BN_set_word(e, RSA_EXPONENT)) {
        BN_free(n); BN_free(e); RSA_free(rsa); free(sig); return false;
    }
    if (RSA_set0_key(rsa, n, e, NULL) != 1) {
        BN_free(n); BN_free(e); RSA_free(rsa); free(sig); return false;
    }

    int rsa_size = RSA_size(rsa);
    if ((int)sig_len != rsa_size) { RSA_free(rsa); free(sig); return false; }
    unsigned char *decoded = malloc((size_t)rsa_size);
    if (!decoded) { RSA_free(rsa); free(sig); return false; }
    int decoded_len = RSA_public_decrypt((int)sig_len, sig, decoded, rsa, RSA_PKCS1_PADDING);
    RSA_free(rsa);
    free(sig);
    if (decoded_len <= 0) { free(decoded); return false; }

    static const unsigned char prefix[] = {
        0x30,0x31,0x30,0x0d,0x06,0x09,0x60,0x86,0x48,0x01,0x65,0x03,0x04,0x02,0x01,0x05,0x00,0x04,0x20
    };
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(message, message_len, digest);
    size_t expected_len = sizeof(prefix) + sizeof(digest);
    bool ok = (decoded_len == (int)expected_len) &&
              memcmp(decoded, prefix, sizeof(prefix)) == 0 &&
              memcmp(decoded + sizeof(prefix), digest, sizeof(digest)) == 0;
    free(decoded);
    return ok;
}

static bool runtime_dir(char out[PATH_MAX]) {
    char self[PATH_MAX];
    ssize_t n = readlink("/proc/self/exe", self, sizeof(self)-1);
    if (n <= 0 || n >= (ssize_t)sizeof(self)) return false;
    self[n] = '\0';
    char *slash = strrchr(self, '/');
    if (!slash) return false;
    *slash = '\0';
    slash = strrchr(self, '/');
    if (!slash) return false;
    *slash = '\0';
    if (strlen(self) >= PATH_MAX) return false;
    strcpy(out, self);
    return true;
}

static bool join_path(char out[PATH_MAX], const char *base, const char *leaf) {
    int n = snprintf(out, PATH_MAX, "%s/%s", base, leaf);
    return n > 0 && n < PATH_MAX;
}

static bool verify_pinned_python_sources(const char *runtime) {
    char path[PATH_MAX];
    if (!join_path(path, runtime, "v24_v6_external_gate_worker.py") ||
        !sha256_file_matches(path, EXPECTED_WORKER_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_proof_reference_closure.py") ||
        !sha256_file_matches(path, EXPECTED_PRC_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_root_attestation.py") ||
        !sha256_file_matches(path, EXPECTED_ROOT_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_governance_foundation.py") ||
        !sha256_file_matches(path, EXPECTED_FOUNDATION_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_decision_apply.py") ||
        !sha256_file_matches(path, EXPECTED_DECISION_APPLY_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_material_surface.py") ||
        !sha256_file_matches(path, EXPECTED_MATERIAL_SURFACE_SHA256)) return false;
    if (!join_path(path, runtime, "v24_v6_normative_clause_projection.py") ||
        !sha256_file_matches(path, EXPECTED_NORMATIVE_PROJECTION_SHA256)) return false;
    if (!join_path(path, runtime, "normative_control_catalog.py") ||
        !sha256_file_matches(path, EXPECTED_NORMATIVE_CATALOG_SHA256)) return false;
    return true;
}

static char *run_worker(
    const char *runtime,
    const char *operation,
    const char *context_path,
    const char *boundary_path,
    const char *reference,
    const char *expected_id,
    const char *expected_digest,
    int *status_out
) {
    char worker[PATH_MAX];
    if (!join_path(worker, runtime, "v24_v6_external_gate_worker.py")) return NULL;
    char *const envp[] = {
        "PATH=/usr/bin:/bin",
        "LC_ALL=C.UTF-8",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        NULL
    };
    char *argv[] = {
        "/usr/bin/python3",
        "-E",
        "-s",
        worker,
        (char *)operation,
        (char *)context_path,
        (char *)boundary_path,
        (char *)reference,
        (char *)expected_id,
        (char *)expected_digest,
        NULL
    };
    return capture_exec(argv, envp, status_out);
}

static char *run_downstream_worker(
    const char *runtime,
    const char *operation,
    const char *context_path,
    const char *boundary_path,
    const char *payload_path,
    int *status_out
) {
    char worker[PATH_MAX];
    if (!join_path(worker, runtime, "v24_v6_external_gate_worker.py")) return NULL;
    char *const envp[] = {
        "PATH=/usr/bin:/bin",
        "LC_ALL=C.UTF-8",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        NULL
    };
    char *argv[] = {
        "/usr/bin/python3",
        "-E",
        "-s",
        worker,
        (char *)operation,
        (char *)context_path,
        (char *)boundary_path,
        (char *)payload_path,
        NULL
    };
    return capture_exec(argv, envp, status_out);
}

static bool write_temp_json(const char *content, char path_out[PATH_MAX]) {
    char tmpl[] = "/tmp/v24-v6-gate-worker-XXXXXX";
    int fd = mkstemp(tmpl);
    if (fd < 0) return false;
    size_t len = strlen(content);
    ssize_t wrote = write(fd, content, len);
    close(fd);
    if (wrote != (ssize_t)len) { unlink(tmpl); return false; }
    strncpy(path_out, tmpl, PATH_MAX-1);
    path_out[PATH_MAX-1] = '\0';
    return true;
}

static int resolve_command(int argc, char **argv) {
    if (argc != 10) {
        deny("ARGUMENT_COUNT_INVALID");
        return 2;
    }
    const char *operation = argv[1];
    const char *context_path = argv[2];
    const char *boundary_path = argv[3];
    const char *reference = argv[4];
    const char *expected_id = argv[5];
    const char *expected_digest = argv[6];
    const char *required_gate_id = argv[7];
    const char *required_gate_version = argv[8];
    const char *mode = argv[9];

    if (strcmp(mode, "enforce") != 0) { deny("ENFORCEMENT_MODE_REQUIRED"); return 1; }
    if (strcmp(required_gate_id, GATE_ID) != 0) { deny("VERIFIER_IDENTITY_MISMATCH"); return 1; }
    if (strcmp(required_gate_version, GATE_VERSION) != 0) { deny("VERIFIER_VERSION_MISMATCH"); return 1; }
    if (!(strcmp(operation, "resolve-governed") == 0 ||
          strcmp(operation, "resolve-independence") == 0 ||
          strcmp(operation, "resolve-currentness") == 0)) {
        deny("OPERATION_UNSUPPORTED"); return 1;
    }
    if (!is_hex64(reference)) { deny("REFERENCE_DIGEST_INVALID"); return 1; }
    if (strcmp(expected_digest, "-") != 0 && !is_hex64(expected_digest)) {
        deny("EXPECTED_DIGEST_INVALID"); return 1;
    }

    char runtime[PATH_MAX];
    if (!runtime_dir(runtime)) { deny("GATE_RUNTIME_ROOT_UNRESOLVED"); return 1; }
    if (!verify_pinned_python_sources(runtime)) { deny("PINNED_SOURCE_DIGEST_MISMATCH"); return 1; }

    int st = 0;
    const char *boundary_filter =
        "["
        "(.governance_generation_id // \"\"),"
        "(.expected_proof_context_digest // \"\"),"
        "(.expected_genesis_scope_digest // \"\"),"
        "((.root_attestation.schema_version // -1)|tostring),"
        "(.root_attestation.key_id // \"\"),"
        "(.root_attestation.algorithm // \"\"),"
        "(.root_attestation.purpose // \"\"),"
        "(.root_attestation.governance_generation_id // \"\"),"
        "(.root_attestation.proof_context_digest // \"\"),"
        "(.root_attestation.genesis_trusted_scope_digest // \"\"),"
        "(.root_attestation.signature_b64 // \"\"),"
        "(((.root_attestation // {})|keys|sort|join(\",\")))"
        "]|@tsv";
    char *boundary_fields = run_jq("-r", boundary_filter, boundary_path, &st);
    if (!boundary_fields || !child_ok(st)) {
        free(boundary_fields); deny("TRUSTED_BOUNDARY_MALFORMED"); return 1;
    }
    char *bf[12] = {0};
    int bcount = split_tsv(boundary_fields, bf, 12);
    if (bcount != 12) { free(boundary_fields); deny("TRUSTED_BOUNDARY_FIELDS_INVALID"); return 1; }

    char *generation = bf[0];
    char *expected_context_digest = bf[1];
    char *expected_scope_digest = bf[2];
    char *schema = bf[3];
    char *key_id = bf[4];
    char *algorithm = bf[5];
    char *purpose = bf[6];
    char *att_generation = bf[7];
    char *att_context_digest = bf[8];
    char *att_scope_digest = bf[9];
    char *signature_b64 = bf[10];
    char *att_keys = bf[11];

    if (!is_hex64(expected_context_digest) || !is_hex64(expected_scope_digest)) {
        free(boundary_fields); deny("TRUSTED_BOUNDARY_DIGEST_INVALID"); return 1;
    }
    if (strcmp(schema, ATTESTATION_SCHEMA) != 0 ||
        strcmp(key_id, KEY_ID) != 0 ||
        strcmp(algorithm, ALGORITHM) != 0 ||
        strcmp(purpose, PURPOSE) != 0 ||
        strcmp(att_keys, ATTESTATION_KEYS) != 0) {
        free(boundary_fields); deny("ROOT_ATTESTATION_IDENTITY_INVALID"); return 1;
    }
    if (strcmp(att_generation, generation) != 0 ||
        strcmp(att_context_digest, expected_context_digest) != 0 ||
        strcmp(att_scope_digest, expected_scope_digest) != 0) {
        free(boundary_fields); deny("ROOT_ATTESTATION_BINDING_MISMATCH"); return 1;
    }

    const char *context_fields_filter =
        "["
        "(.governance_generation_id // \"\"),"
        "(.context_digest // \"\"),"
        "(.genesis_trusted_scope.scope_digest // \"\"),"
        "(.genesis_trusted_scope.governance_generation_id // \"\")"
        "]|@tsv";
    char *context_fields = run_jq("-r", context_fields_filter, context_path, &st);
    if (!context_fields || !child_ok(st)) {
        free(boundary_fields); free(context_fields); deny("PROOF_CONTEXT_MALFORMED"); return 1;
    }
    char *cf[4] = {0};
    int ccount = split_tsv(context_fields, cf, 4);
    if (ccount != 4) {
        free(boundary_fields); free(context_fields); deny("PROOF_CONTEXT_FIELDS_INVALID"); return 1;
    }
    char *ctx_generation = cf[0];
    char *ctx_digest_field = cf[1];
    char *scope_digest_field = cf[2];
    char *scope_generation = cf[3];

    if (strcmp(ctx_generation, generation) != 0 || strcmp(scope_generation, generation) != 0) {
        free(boundary_fields); free(context_fields); deny("PROOF_CONTEXT_GENERATION_MISMATCH"); return 1;
    }
    if (!is_hex64(ctx_digest_field) || !is_hex64(scope_digest_field)) {
        free(boundary_fields); free(context_fields); deny("PROOF_CONTEXT_DIGEST_FIELD_INVALID"); return 1;
    }

    char *canonical_context = run_jq("-cS", "del(.context_digest)", context_path, &st);
    if (!canonical_context || !child_ok(st)) {
        free(boundary_fields); free(context_fields); free(canonical_context);
        deny("PROOF_CONTEXT_CANONICALIZATION_FAILED"); return 1;
    }
    char recomputed_context[65];
    sha256_hex_bytes((unsigned char *)canonical_context, strlen(canonical_context), recomputed_context);

    char *canonical_scope = run_jq("-cS", ".genesis_trusted_scope|del(.scope_digest)", context_path, &st);
    if (!canonical_scope || !child_ok(st)) {
        free(boundary_fields); free(context_fields); free(canonical_context); free(canonical_scope);
        deny("GENESIS_SCOPE_CANONICALIZATION_FAILED"); return 1;
    }
    char recomputed_scope[65];
    sha256_hex_bytes((unsigned char *)canonical_scope, strlen(canonical_scope), recomputed_scope);

    if (strcmp(recomputed_context, ctx_digest_field) != 0 ||
        strcmp(ctx_digest_field, expected_context_digest) != 0) {
        free(boundary_fields); free(context_fields); free(canonical_context); free(canonical_scope);
        deny("EXTERNAL_CONTEXT_DIGEST_MISMATCH"); return 1;
    }
    if (strcmp(recomputed_scope, scope_digest_field) != 0 ||
        strcmp(scope_digest_field, expected_scope_digest) != 0) {
        free(boundary_fields); free(context_fields); free(canonical_context); free(canonical_scope);
        deny("EXTERNAL_SCOPE_DIGEST_MISMATCH"); return 1;
    }

    char *attestation_material = run_jq(
        "-cS",
        ".root_attestation|{algorithm,genesis_trusted_scope_digest,governance_generation_id,key_id,proof_context_digest,purpose,schema_version}",
        boundary_path,
        &st
    );
    if (!attestation_material || !child_ok(st)) {
        free(boundary_fields); free(context_fields); free(canonical_context); free(canonical_scope); free(attestation_material);
        deny("ROOT_ATTESTATION_CANONICALIZATION_FAILED"); return 1;
    }
    if (!verify_rsa_pkcs1_sha256((unsigned char *)attestation_material, strlen(attestation_material), signature_b64)) {
        free(boundary_fields); free(context_fields); free(canonical_context); free(canonical_scope); free(attestation_material);
        deny("ROOT_ATTESTATION_SIGNATURE_INVALID"); return 1;
    }

    free(canonical_context);
    free(canonical_scope);
    free(attestation_material);

    char *worker_output = run_worker(
        runtime, operation, context_path, boundary_path, reference, expected_id, expected_digest, &st
    );
    if (!worker_output || !child_ok(st)) {
        free(boundary_fields); free(context_fields); free(worker_output);
        deny("EXTERNAL_GATE_WORKER_FAILED"); return 1;
    }

    char worker_tmp[PATH_MAX];
    if (!write_temp_json(worker_output, worker_tmp)) {
        free(boundary_fields); free(context_fields); free(worker_output);
        deny("EXTERNAL_GATE_WORKER_OUTPUT_UNMATERIALIZED"); return 1;
    }
    const char *worker_filter =
        "["
        "(.qualified|tostring),"
        "(.state // \"\"),"
        "(.reference_digest // \"\"),"
        "(.authority_effect // \"\"),"
        "(.input_binding.governance_generation_id // \"\"),"
        "(.input_binding.context_digest // \"\"),"
        "(.input_binding.genesis_trusted_scope_digest // \"\"),"
        "(.input_binding.expected_id // \"\"),"
        "(.input_binding.expected_digest // \"\")"
        "]|@tsv";
    char *worker_fields = run_jq("-r", worker_filter, worker_tmp, &st);
    unlink(worker_tmp);
    if (!worker_fields || !child_ok(st)) {
        free(boundary_fields); free(context_fields); free(worker_output); free(worker_fields);
        deny("EXTERNAL_GATE_WORKER_OUTPUT_MALFORMED"); return 1;
    }
    char *wf[9] = {0};
    int wcount = split_tsv(worker_fields, wf, 9);
    if (wcount != 9 ||
        strcmp(wf[0], "true") != 0 ||
        strcmp(wf[1], "PROOF_REFERENCE_CLOSED") != 0 ||
        strcmp(wf[2], reference) != 0 ||
        strcmp(wf[3], AUTHORITY_EFFECT) != 0 ||
        strcmp(wf[4], generation) != 0 ||
        strcmp(wf[5], expected_context_digest) != 0 ||
        strcmp(wf[6], expected_scope_digest) != 0 ||
        strcmp(wf[7], expected_id) != 0 ||
        strcmp(wf[8], expected_digest) != 0) {
        free(boundary_fields); free(context_fields); free(worker_output); free(worker_fields);
        deny("EXTERNAL_GATE_WORKER_DECISION_REJECTED"); return 1;
    }

    char worker_digest[65];
    sha256_hex_bytes((unsigned char *)worker_output, strlen(worker_output), worker_digest);
    printf("{\"authority_effect\":\"%s\",\"build_input_sha256\":\"%s\","
           "\"construction_authoritative\":true,\"context_digest\":\"%s\","
           "\"decision\":\"ALLOW\",\"gate_id\":\"%s\",\"gate_version\":\"%s\","
           "\"reference_digest\":\"%s\",\"scope_digest\":\"%s\","
           "\"worker_result_sha256\":\"%s\"}\n",
           AUTHORITY_EFFECT, BUILD_INPUT_SHA256, expected_context_digest,
           GATE_ID, GATE_VERSION, reference, expected_scope_digest, worker_digest);

    free(boundary_fields);
    free(context_fields);
    free(worker_output);
    free(worker_fields);
    return 0;
}

static int downstream_command(int argc, char **argv) {
    if (argc != 11) {
        deny("ARGUMENT_COUNT_INVALID");
        return 2;
    }
    const char *operation = argv[1];
    const char *context_path = argv[2];
    const char *boundary_path = argv[3];
    const char *payload_path = argv[4];
    const char *probe_reference = argv[5];
    const char *probe_expected_id = argv[6];
    const char *probe_expected_digest = argv[7];
    const char *required_gate_id = argv[8];
    const char *required_gate_version = argv[9];
    const char *mode = argv[10];

    if (strcmp(mode, "enforce") != 0) { deny("ENFORCEMENT_MODE_REQUIRED"); return 1; }
    if (strcmp(required_gate_id, GATE_ID) != 0) { deny("VERIFIER_IDENTITY_MISMATCH"); return 1; }
    if (strcmp(required_gate_version, GATE_VERSION) != 0) { deny("VERIFIER_VERSION_MISMATCH"); return 1; }
    if (!(strcmp(operation, "evaluate-decision-apply") == 0 ||
          strcmp(operation, "validate-normative-coverage") == 0)) {
        deny("OPERATION_UNSUPPORTED"); return 1;
    }
    if (!is_hex64(probe_reference)) { deny("REFERENCE_DIGEST_INVALID"); return 1; }
    if (strcmp(probe_expected_digest, "-") != 0 && !is_hex64(probe_expected_digest)) {
        deny("EXPECTED_DIGEST_INVALID"); return 1;
    }

    char runtime[PATH_MAX];
    if (!runtime_dir(runtime)) { deny("GATE_RUNTIME_ROOT_UNRESOLVED"); return 1; }
    if (!verify_pinned_python_sources(runtime)) { deny("PINNED_SOURCE_DIGEST_MISMATCH"); return 1; }

    char self[PATH_MAX];
    ssize_t self_len = readlink("/proc/self/exe", self, sizeof(self)-1);
    if (self_len <= 0 || self_len >= (ssize_t)sizeof(self)) {
        deny("GATE_SELF_IDENTITY_UNRESOLVED"); return 1;
    }
    self[self_len] = '\0';

    char *const envp[] = {
        "PATH=/usr/bin:/bin",
        "LC_ALL=C.UTF-8",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        NULL
    };
    char *probe_argv[] = {
        self,
        "resolve-governed",
        (char *)context_path,
        (char *)boundary_path,
        (char *)probe_reference,
        (char *)probe_expected_id,
        (char *)probe_expected_digest,
        GATE_ID,
        GATE_VERSION,
        "enforce",
        NULL
    };
    int st = 0;
    char *probe_output = capture_exec(probe_argv, envp, &st);
    if (!probe_output || !child_ok(st)) {
        free(probe_output); deny("EXTERNAL_CONTEXT_PROBE_REJECTED"); return 1;
    }
    char probe_tmp[PATH_MAX];
    if (!write_temp_json(probe_output, probe_tmp)) {
        free(probe_output); deny("EXTERNAL_CONTEXT_PROBE_UNMATERIALIZED"); return 1;
    }
    const char *probe_filter =
        "["
        "(.decision // \"\"),"
        "(.construction_authoritative|tostring),"
        "(.gate_id // \"\"),"
        "(.gate_version // \"\"),"
        "(.context_digest // \"\"),"
        "(.scope_digest // \"\")"
        "]|@tsv";
    char *probe_fields = run_jq("-r", probe_filter, probe_tmp, &st);
    unlink(probe_tmp);
    free(probe_output);
    if (!probe_fields || !child_ok(st)) {
        free(probe_fields); deny("EXTERNAL_CONTEXT_PROBE_MALFORMED"); return 1;
    }
    char *pf[6] = {0};
    int pcount = split_tsv(probe_fields, pf, 6);
    if (pcount != 6 ||
        strcmp(pf[0], "ALLOW") != 0 ||
        strcmp(pf[1], "true") != 0 ||
        strcmp(pf[2], GATE_ID) != 0 ||
        strcmp(pf[3], GATE_VERSION) != 0 ||
        !is_hex64(pf[4]) || !is_hex64(pf[5])) {
        free(probe_fields); deny("EXTERNAL_CONTEXT_PROBE_INVALID"); return 1;
    }
    char expected_context_digest[65];
    char expected_scope_digest[65];
    strncpy(expected_context_digest, pf[4], 64); expected_context_digest[64] = '\0';
    strncpy(expected_scope_digest, pf[5], 64); expected_scope_digest[64] = '\0';
    free(probe_fields);

    int generation_status = 0;
    char *generation = run_jq("-r", ".governance_generation_id // \"\"", context_path, &generation_status);
    if (!generation || !child_ok(generation_status) || generation[0] == '\0') {
        free(generation); deny("PROOF_CONTEXT_GENERATION_INVALID"); return 1;
    }

    size_t payload_len = 0;
    unsigned char *payload_bytes = read_file(payload_path, &payload_len);
    if (!payload_bytes) {
        free(generation); deny("DOWNSTREAM_PAYLOAD_UNREADABLE"); return 1;
    }
    char payload_digest[65];
    sha256_hex_bytes(payload_bytes, payload_len, payload_digest);
    free(payload_bytes);

    char *worker_output = run_downstream_worker(
        runtime, operation, context_path, boundary_path, payload_path, &st
    );
    if (!worker_output || !child_ok(st)) {
        free(generation); free(worker_output);
        deny("EXTERNAL_GATE_WORKER_FAILED"); return 1;
    }
    char worker_tmp[PATH_MAX];
    if (!write_temp_json(worker_output, worker_tmp)) {
        free(generation); free(worker_output);
        deny("EXTERNAL_GATE_WORKER_OUTPUT_UNMATERIALIZED"); return 1;
    }
    const char *worker_filter =
        "["
        "(.success|tostring),"
        "(.state // \"\"),"
        "(.authority_effect // \"\"),"
        "(.input_binding.governance_generation_id // \"\"),"
        "(.input_binding.context_digest // \"\"),"
        "(.input_binding.genesis_trusted_scope_digest // \"\"),"
        "(.payload_sha256 // \"\")"
        "]|@tsv";
    char *worker_fields = run_jq("-r", worker_filter, worker_tmp, &st);
    unlink(worker_tmp);
    if (!worker_fields || !child_ok(st)) {
        free(generation); free(worker_output); free(worker_fields);
        deny("EXTERNAL_GATE_WORKER_OUTPUT_MALFORMED"); return 1;
    }
    char *wf[7] = {0};
    int wcount = split_tsv(worker_fields, wf, 7);
    if (wcount != 7 ||
        strcmp(wf[0], "true") != 0 ||
        wf[1][0] == '\0' ||
        strcmp(wf[2], AUTHORITY_EFFECT) != 0 ||
        strcmp(wf[3], generation) != 0 ||
        strcmp(wf[4], expected_context_digest) != 0 ||
        strcmp(wf[5], expected_scope_digest) != 0 ||
        strcmp(wf[6], payload_digest) != 0) {
        free(generation); free(worker_output); free(worker_fields);
        deny("EXTERNAL_GATE_WORKER_DECISION_REJECTED"); return 1;
    }

    char worker_digest[65];
    sha256_hex_bytes((unsigned char *)worker_output, strlen(worker_output), worker_digest);
    printf("{\"authority_effect\":\"%s\",\"build_input_sha256\":\"%s\","
           "\"construction_authoritative\":true,\"context_digest\":\"%s\","
           "\"decision\":\"ALLOW\",\"gate_id\":\"%s\",\"gate_version\":\"%s\","
           "\"operation\":\"%s\",\"payload_sha256\":\"%s\",\"scope_digest\":\"%s\","
           "\"worker_result_sha256\":\"%s\"}\n",
           AUTHORITY_EFFECT, BUILD_INPUT_SHA256, expected_context_digest,
           GATE_ID, GATE_VERSION, operation, payload_digest, expected_scope_digest, worker_digest);

    free(generation);
    free(worker_output);
    free(worker_fields);
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--identity") == 0) {
        printf("{\"authority_effect\":\"%s\",\"build_input_sha256\":\"%s\","
               "\"gate_id\":\"%s\",\"gate_version\":\"%s\"}\n",
               AUTHORITY_EFFECT, BUILD_INPUT_SHA256, GATE_ID, GATE_VERSION);
        return 0;
    }
    if (argc >= 2 && strcmp(argv[1], "consume-verdict") == 0) {
        deny("CALLER_SUPPLIED_VERDICT_UNSUPPORTED");
        return 1;
    }
    if (argc >= 2 &&
        (strcmp(argv[1], "evaluate-decision-apply") == 0 ||
         strcmp(argv[1], "validate-normative-coverage") == 0)) {
        return downstream_command(argc, argv);
    }
    return resolve_command(argc, argv);
}
