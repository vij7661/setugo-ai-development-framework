#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <openssl/sha.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#define CONSUMER_ID "V24-V6-TRUSTED-RECORD-CONSUMER"
#define CONSUMER_VERSION "1"
#define SERVICE_ID "V24-V6-TRUSTED-AUTHORITY-SERVICE"
#define SERVICE_VERSION "3"
#define AUTHORITY_EFFECT "NONE_EVIDENCE_ONLY"
#define CONTROL_SOCKET "/run/v24-v6-authority/private/control.sock"
#define PRIVATE_DIR "/run/v24-v6-authority/private"
#define RECORD_DIR "/run/v24-v6-authority/private/records"
#define CONSUMED_DIR "/run/v24-v6-authority/private/consumed"
#define MAX_FIELD (8U * 1024U * 1024U)

#ifndef BUILD_INPUT_SHA256
#define BUILD_INPUT_SHA256 "UNBUILT"
#endif
#ifndef EXPECTED_SERVICE_BUILD_INPUT_SHA256
#define EXPECTED_SERVICE_BUILD_INPUT_SHA256 "UNBUILT"
#endif

static void sha256_hex(const unsigned char *data, size_t len, char out[65]) {
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(data, len, digest);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        sprintf(out + (i * 2), "%02x", digest[i]);
    }
    out[64] = '\0';
}

static bool send_all(int fd, const void *buf, size_t len) {
    const unsigned char *p = buf;
    while (len > 0) {
        ssize_t n = send(fd, p, len, MSG_NOSIGNAL);
        if (n < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (n == 0) return false;
        p += (size_t)n;
        len -= (size_t)n;
    }
    return true;
}

static bool recv_exact(int fd, unsigned char *buf, size_t len) {
    size_t off = 0;
    while (off < len) {
        ssize_t n = recv(fd, buf + off, len - off, 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (n == 0) return false;
        off += (size_t)n;
    }
    return true;
}

static bool recv_line(int fd, char *buf, size_t cap) {
    if (cap < 2) return false;
    size_t n = 0;
    while (n + 1 < cap) {
        unsigned char c = 0;
        ssize_t got = recv(fd, &c, 1, 0);
        if (got < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (got == 0) return false;
        if (c == '\n') {
            buf[n] = '\0';
            return true;
        }
        if (c == '\r') continue;
        buf[n++] = (char)c;
    }
    return false;
}

static bool parse_size(const char *s, size_t *out) {
    if (!s || !*s) return false;
    errno = 0;
    char *end = NULL;
    unsigned long long v = strtoull(s, &end, 10);
    if (errno != 0 || !end || *end != '\0' || v > MAX_FIELD) return false;
    *out = (size_t)v;
    return true;
}

static bool is_hex64(const char *s) {
    if (!s || strlen(s) != 64) return false;
    for (size_t i = 0; i < 64; ++i) {
        char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

static bool valid_operation(const char *op) {
    return strcmp(op, "resolve-governed") == 0 ||
           strcmp(op, "resolve-independence") == 0 ||
           strcmp(op, "resolve-currentness") == 0 ||
           strcmp(op, "evaluate-decision-apply") == 0 ||
           strcmp(op, "validate-normative-coverage") == 0;
}

static bool ensure_root_dir(const char *path, mode_t mode) {
    struct stat st;
    if (lstat(path, &st) != 0) return false;
    if (!S_ISDIR(st.st_mode) || S_ISLNK(st.st_mode) ||
        st.st_uid != 0 || st.st_gid != 0 || (st.st_mode & 0022) != 0) {
        return false;
    }
    return chmod(path, mode) == 0;
}

static bool prepare_runtime(void) {
    if (geteuid() != 0) return false;
    if (!ensure_root_dir(PRIVATE_DIR, 0700)) return false;
    if (!ensure_root_dir(RECORD_DIR, 0700)) return false;
    if (!ensure_root_dir(CONSUMED_DIR, 0700)) return false;
    return true;
}

static bool field_value(const char *body, const char *key, char *out, size_t cap) {
    char needle[128];
    int nn = snprintf(needle, sizeof(needle), "%s=", key);
    if (nn <= 0 || (size_t)nn >= sizeof(needle)) return false;
    const char *p = strstr(body, needle);
    if (!p || (p != body && p[-1] != '\n')) return false;
    p += nn;
    const char *end = strchr(p, '\n');
    if (!end) return false;
    size_t len = (size_t)(end - p);
    if (len == 0 || len >= cap) return false;
    memcpy(out, p, len);
    out[len] = '\0';
    return true;
}

static bool read_record(const char *path, unsigned char **data_out, size_t *len_out) {
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) return false;
    struct stat st;
    if (fstat(fd, &st) != 0 || !S_ISREG(st.st_mode) ||
        st.st_uid != 0 || st.st_gid != 0 || (st.st_mode & 0077) != 0 ||
        st.st_size <= 0 || st.st_size > 8192) {
        close(fd);
        return false;
    }
    size_t len = (size_t)st.st_size;
    unsigned char *data = malloc(len + 1);
    if (!data) {
        close(fd);
        return false;
    }
    size_t off = 0;
    while (off < len) {
        ssize_t n = read(fd, data + off, len - off);
        if (n < 0) {
            if (errno == EINTR) continue;
            free(data);
            close(fd);
            return false;
        }
        if (n == 0) {
            free(data);
            close(fd);
            return false;
        }
        off += (size_t)n;
    }
    close(fd);
    data[len] = '\0';
    *data_out = data;
    *len_out = len;
    return true;
}

static bool send_result(
    int fd,
    bool authoritative,
    const char *decision,
    const char *reason,
    const char *record_id,
    const char *request_digest,
    const char *gate_digest,
    const char *operation
) {
    char body[4096];
    int n = snprintf(
        body, sizeof(body),
        "{\"authority_effect\":\"%s\",\"construction_authoritative\":%s,"
        "\"consumer_authoritative\":%s,\"consumer_build_input_sha256\":\"%s\","
        "\"consumer_id\":\"%s\",\"consumer_version\":\"%s\","
        "\"decision\":\"%s\",\"gate_result_sha256\":\"%s\","
        "\"operation\":\"%s\",\"reason\":\"%s\",\"record_state\":\"%s\","
        "\"request_sha256\":\"%s\",\"service_authoritative\":%s,"
        "\"service_build_input_sha256\":\"%s\",\"service_id\":\"%s\","
        "\"service_version\":\"%s\",\"trusted_record_id\":\"%s\"}",
        AUTHORITY_EFFECT,
        authoritative ? "true" : "false",
        authoritative ? "true" : "false",
        BUILD_INPUT_SHA256,
        CONSUMER_ID,
        CONSUMER_VERSION,
        decision ? decision : "DENY",
        gate_digest ? gate_digest : "-",
        operation ? operation : "-",
        reason ? reason : "-",
        authoritative ? "CONSUMED" : "UNCONSUMED",
        request_digest ? request_digest : "-",
        authoritative ? "true" : "false",
        EXPECTED_SERVICE_BUILD_INPUT_SHA256,
        SERVICE_ID,
        SERVICE_VERSION,
        record_id ? record_id : "-"
    );
    if (n <= 0 || (size_t)n >= sizeof(body)) return false;
    char header[64];
    int hn = snprintf(header, sizeof(header), "%d\n", n);
    return hn > 0 && send_all(fd, header, (size_t)hn) &&
           send_all(fd, body, (size_t)n);
}

static bool recompute_request_digest(
    const char *operation,
    const char *reference,
    const char *expected_id,
    const char *expected_digest,
    const unsigned char *context,
    size_t context_len,
    const unsigned char *boundary,
    size_t boundary_len,
    const unsigned char *payload,
    size_t payload_len,
    char out[65]
) {
    size_t len = strlen(operation) + strlen(reference) + strlen(expected_id) +
                 strlen(expected_digest) + 4 + context_len + boundary_len + payload_len;
    unsigned char *buf = malloc(len);
    if (!buf) return false;
    size_t off = 0;
    const char *parts[] = {operation, reference, expected_id, expected_digest};
    for (size_t i = 0; i < 4; ++i) {
        size_t n = strlen(parts[i]);
        memcpy(buf + off, parts[i], n);
        off += n;
        buf[off++] = '\0';
    }
    memcpy(buf + off, context, context_len);
    off += context_len;
    memcpy(buf + off, boundary, boundary_len);
    off += boundary_len;
    if (payload_len) {
        memcpy(buf + off, payload, payload_len);
        off += payload_len;
    }
    sha256_hex(buf, off, out);
    free(buf);
    return true;
}

static bool consume_exact_record(
    const char *record_id,
    const char *request_digest,
    char decision_out[32],
    char gate_out[65]
) {
    char src[PATH_MAX], dst[PATH_MAX];
    if (snprintf(src, sizeof(src), "%s/%s.record", RECORD_DIR, record_id) >= (int)sizeof(src) ||
        snprintf(dst, sizeof(dst), "%s/%s.record", CONSUMED_DIR, record_id) >= (int)sizeof(dst)) {
        return false;
    }

    unsigned char *data = NULL;
    size_t len = 0;
    if (!read_record(src, &data, &len)) return false;

    char schema[128], rec_id[65], service_id[128], service_version[64];
    char build[65], request[65], decision[32], gate[65], effect[64];
    bool valid =
        field_value((char *)data, "schema", schema, sizeof(schema)) &&
        field_value((char *)data, "record_id", rec_id, sizeof(rec_id)) &&
        field_value((char *)data, "service_id", service_id, sizeof(service_id)) &&
        field_value((char *)data, "service_version", service_version, sizeof(service_version)) &&
        field_value((char *)data, "service_build_input_sha256", build, sizeof(build)) &&
        field_value((char *)data, "request_sha256", request, sizeof(request)) &&
        field_value((char *)data, "decision", decision, sizeof(decision)) &&
        field_value((char *)data, "gate_result_sha256", gate, sizeof(gate)) &&
        field_value((char *)data, "authority_effect", effect, sizeof(effect)) &&
        strcmp(schema, "V24_V6_S8_AUTHORITY_RECORD_V1") == 0 &&
        strcmp(rec_id, record_id) == 0 &&
        strcmp(service_id, SERVICE_ID) == 0 &&
        strcmp(service_version, SERVICE_VERSION) == 0 &&
        strcmp(build, EXPECTED_SERVICE_BUILD_INPUT_SHA256) == 0 &&
        strcmp(request, request_digest) == 0 &&
        is_hex64(gate) &&
        strcmp(effect, AUTHORITY_EFFECT) == 0 &&
        (strcmp(decision, "ALLOW") == 0 || strcmp(decision, "DENY") == 0);
    free(data);
    if (!valid) return false;

    if (rename(src, dst) != 0) return false;
    strncpy(decision_out, decision, 31);
    decision_out[31] = '\0';
    strncpy(gate_out, gate, 64);
    gate_out[64] = '\0';
    return true;
}

static void handle_control(int fd) {
    struct ucred cred;
    socklen_t cred_len = sizeof(cred);
    if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &cred_len) != 0 ||
        cred_len != sizeof(cred) || cred.uid != 0) {
        send_result(fd, false, "DENY", "TRUSTED_CONTROL_PEER_REJECTED",
                    NULL, NULL, NULL, NULL);
        return;
    }

    char magic[64], record_id[128], operation[96], reference[256];
    char expected_id[512], expected_digest[256];
    char context_len_s[64], boundary_len_s[64], payload_len_s[64];

    if (!recv_line(fd, magic, sizeof(magic)) ||
        !recv_line(fd, record_id, sizeof(record_id)) ||
        !recv_line(fd, operation, sizeof(operation)) ||
        !recv_line(fd, reference, sizeof(reference)) ||
        !recv_line(fd, expected_id, sizeof(expected_id)) ||
        !recv_line(fd, expected_digest, sizeof(expected_digest)) ||
        !recv_line(fd, context_len_s, sizeof(context_len_s)) ||
        !recv_line(fd, boundary_len_s, sizeof(boundary_len_s)) ||
        !recv_line(fd, payload_len_s, sizeof(payload_len_s))) {
        send_result(fd, true, "DENY", "CONTROL_HEADER_MALFORMED",
                    record_id, NULL, NULL, operation);
        return;
    }

    if (strcmp(magic, "V24-V6-S9-CONSUME/1") != 0 ||
        !is_hex64(record_id) ||
        !valid_operation(operation) ||
        !is_hex64(reference) ||
        (strcmp(expected_digest, "-") != 0 && !is_hex64(expected_digest))) {
        send_result(fd, true, "DENY", "CONTROL_HEADER_INVALID",
                    record_id, NULL, NULL, operation);
        return;
    }

    size_t context_len = 0, boundary_len = 0, payload_len = 0;
    if (!parse_size(context_len_s, &context_len) ||
        !parse_size(boundary_len_s, &boundary_len) ||
        !parse_size(payload_len_s, &payload_len) ||
        context_len == 0 || boundary_len == 0) {
        send_result(fd, true, "DENY", "CONTROL_LENGTH_INVALID",
                    record_id, NULL, NULL, operation);
        return;
    }

    unsigned char *context = malloc(context_len);
    unsigned char *boundary = malloc(boundary_len);
    unsigned char *payload = payload_len ? malloc(payload_len) : NULL;
    if (!context || !boundary || (payload_len && !payload)) {
        free(context);
        free(boundary);
        free(payload);
        send_result(fd, true, "DENY", "CONTROL_ALLOCATION_FAILED",
                    record_id, NULL, NULL, operation);
        return;
    }

    if (!recv_exact(fd, context, context_len) ||
        !recv_exact(fd, boundary, boundary_len) ||
        (payload_len && !recv_exact(fd, payload, payload_len))) {
        free(context);
        free(boundary);
        free(payload);
        send_result(fd, true, "DENY", "CONTROL_BODY_TRUNCATED",
                    record_id, NULL, NULL, operation);
        return;
    }

    char request_digest[65];
    bool bound = recompute_request_digest(
        operation, reference, expected_id, expected_digest,
        context, context_len, boundary, boundary_len,
        payload, payload_len, request_digest
    );
    free(context);
    free(boundary);
    free(payload);
    if (!bound) {
        send_result(fd, true, "DENY", "CONTROL_BINDING_FAILED",
                    record_id, NULL, NULL, operation);
        return;
    }

    char decision[32], gate[65];
    if (!consume_exact_record(record_id, request_digest, decision, gate)) {
        send_result(fd, true, "DENY", "AUTHORITY_RECORD_BINDING_OR_REPLAY_REJECTED",
                    record_id, request_digest, NULL, operation);
        return;
    }

    send_result(fd, true, decision,
                strcmp(decision, "ALLOW") == 0
                    ? "TRUSTED_IN_SERVICE_CONSUME_ALLOWED"
                    : "TRUSTED_IN_SERVICE_CONSUME_DENIED",
                record_id, request_digest, gate, operation);
}

static int serve(void) {
    if (!prepare_runtime()) {
        fprintf(stderr, "trusted record consumer requires root-private runtime\n");
        return 2;
    }
    unlink(CONTROL_SOCKET);
    int s = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (s < 0) return 2;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, CONTROL_SOCKET, sizeof(addr.sun_path) - 1);
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) != 0 ||
        chown(CONTROL_SOCKET, 0, 0) != 0 ||
        chmod(CONTROL_SOCKET, 0600) != 0 ||
        listen(s, 8) != 0) {
        unlink(CONTROL_SOCKET);
        close(s);
        return 2;
    }

    signal(SIGPIPE, SIG_IGN);
    while (1) {
        int c = accept4(s, NULL, NULL, SOCK_CLOEXEC);
        if (c < 0) {
            if (errno == EINTR) continue;
            break;
        }
        handle_control(c);
        close(c);
    }

    unlink(CONTROL_SOCKET);
    close(s);
    return 2;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--identity") == 0) {
        printf("{\"authority_effect\":\"%s\",\"consumer_build_input_sha256\":\"%s\","
               "\"consumer_id\":\"%s\",\"consumer_version\":\"%s\","
               "\"expected_service_build_input_sha256\":\"%s\","
               "\"service_id\":\"%s\",\"service_version\":\"%s\"}\n",
               AUTHORITY_EFFECT, BUILD_INPUT_SHA256,
               CONSUMER_ID, CONSUMER_VERSION,
               EXPECTED_SERVICE_BUILD_INPUT_SHA256,
               SERVICE_ID, SERVICE_VERSION);
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "--serve") == 0) {
        return serve();
    }
    printf("{\"authority_effect\":\"%s\",\"construction_authoritative\":false,"
           "\"consumer_authoritative\":false,\"decision\":\"DENY\","
           "\"reason\":\"DIRECT_CONSUMER_UNSUPPORTED\"}\n",
           AUTHORITY_EFFECT);
    return 1;
}
