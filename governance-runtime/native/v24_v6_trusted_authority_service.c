#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <openssl/sha.h>
#include <pwd.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>

#define SERVICE_ID "V24-V6-TRUSTED-AUTHORITY-SERVICE"
#define SERVICE_VERSION "1"
#define AUTHORITY_EFFECT "NONE_EVIDENCE_ONLY"
#define SOCKET_PATH "/run/v24-v6-authority/service.sock"
#define PID_PATH "/run/v24-v6-authority/service.pid"
#define PRIVATE_DIR "/run/v24-v6-authority/private"
#define GATE_PATH "/opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate"
#define GATE_ID "V24-V6-EXTERNAL-AUTHORITY-GATE"
#define GATE_VERSION "1"
#define CANDIDATE_USER "v24candidate"
#define MAX_FIELD (8U * 1024U * 1024U)
#define MAX_CAPTURE (8U * 1024U * 1024U)

static void sha256_hex(const unsigned char *data, size_t len, char out[65]) {
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(data, len, digest);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) sprintf(out + (i * 2), "%02x", digest[i]);
    out[64] = '\0';
}

static bool send_all(int fd, const void *buf, size_t len) {
    const unsigned char *p = buf;
    while (len > 0) {
        ssize_t n = send(fd, p, len, MSG_NOSIGNAL);
        if (n < 0) { if (errno == EINTR) continue; return false; }
        if (n == 0) return false;
        p += (size_t)n; len -= (size_t)n;
    }
    return true;
}

static bool write_all_fd(int fd, const void *buf, size_t len) {
    const unsigned char *p = buf;
    while (len > 0) {
        ssize_t n = write(fd, p, len);
        if (n < 0) { if (errno == EINTR) continue; return false; }
        if (n == 0) return false;
        p += (size_t)n; len -= (size_t)n;
    }
    return true;
}

static bool recv_exact(int fd, unsigned char *buf, size_t len) {
    size_t off = 0;
    while (off < len) {
        ssize_t n = recv(fd, buf + off, len - off, 0);
        if (n < 0) { if (errno == EINTR) continue; return false; }
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
        if (got < 0) { if (errno == EINTR) continue; return false; }
        if (got == 0) return false;
        if (c == '\n') { buf[n] = '\0'; return true; }
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

static bool is_hex64_or_dash(const char *s) {
    if (strcmp(s, "-") == 0) return true;
    if (strlen(s) != 64) return false;
    for (size_t i = 0; i < 64; ++i) {
        char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

static bool ensure_root_dir(const char *path, mode_t mode) {
    struct stat st;
    if (lstat(path, &st) != 0) {
        if (errno != ENOENT || mkdir(path, mode) != 0) return false;
        if (lstat(path, &st) != 0) return false;
    }
    if (!S_ISDIR(st.st_mode) || S_ISLNK(st.st_mode) || st.st_uid != 0 || st.st_gid != 0) return false;
    if ((st.st_mode & 0022) != 0) return false;
    if (chmod(path, mode) != 0) return false;
    return true;
}

static bool prepare_runtime(void) {
    if (geteuid() != 0) return false;
    if (!ensure_root_dir("/run/v24-v6-authority", 0755)) return false;
    if (!ensure_root_dir(PRIVATE_DIR, 0700)) return false;
    return true;
}

static bool materialize_private(const unsigned char *data, size_t len, const char *tag, char out[PATH_MAX]) {
    if (snprintf(out, PATH_MAX, "%s/%s-XXXXXX", PRIVATE_DIR, tag) >= PATH_MAX) return false;
    int fd = mkstemp(out);
    if (fd < 0) return false;
    bool ok = fchmod(fd, 0600) == 0 && write_all_fd(fd, data, len);
    if (ok) ok = fsync(fd) == 0;
    close(fd);
    if (!ok) { unlink(out); return false; }
    return true;
}

static char *capture_exec(char *const argv[], int *status_out) {
    int pipefd[2];
    if (pipe(pipefd) != 0) return NULL;
    pid_t pid = fork();
    if (pid < 0) { close(pipefd[0]); close(pipefd[1]); return NULL; }
    if (pid == 0) {
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[0]); close(pipefd[1]);
        char *const envp[] = {
            "PATH=/usr/bin:/bin", "LC_ALL=C.UTF-8",
            "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", NULL
        };
        execve(GATE_PATH, argv, envp);
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
        if (n < 0) { if (errno == EINTR) continue; free(buf); close(pipefd[0]); return NULL; }
        if (n == 0) break;
        len += (size_t)n;
    }
    close(pipefd[0]);
    int st = 0;
    if (waitpid(pid, &st, 0) < 0) { free(buf); return NULL; }
    buf[len] = '\0';
    while (len > 0 && (buf[len-1] == '\n' || buf[len-1] == '\r')) buf[--len] = '\0';
    if (status_out) *status_out = st;
    return buf;
}

static bool child_ok(int status) {
    return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

static bool send_response(int fd, const char *decision, const char *reason,
                          const char *request_digest, const char *gate_digest) {
    char json[2048];
    int n = snprintf(
        json, sizeof(json),
        "{\"authority_effect\":\"%s\",\"construction_authoritative\":true,"
        "\"decision\":\"%s\",\"gate_result_sha256\":\"%s\","
        "\"request_sha256\":\"%s\",\"service_authoritative\":true,"
        "\"service_id\":\"%s\",\"service_version\":\"%s\",\"reason\":\"%s\"}",
        AUTHORITY_EFFECT, decision, gate_digest ? gate_digest : "-",
        request_digest ? request_digest : "-", SERVICE_ID, SERVICE_VERSION,
        reason ? reason : "-"
    );
    if (n <= 0 || (size_t)n >= sizeof(json)) return false;
    char header[64];
    int hn = snprintf(header, sizeof(header), "%d\n", n);
    return hn > 0 && send_all(fd, header, (size_t)hn) && send_all(fd, json, (size_t)n);
}

static bool valid_operation(const char *op) {
    return strcmp(op, "resolve-governed") == 0 ||
           strcmp(op, "resolve-independence") == 0 ||
           strcmp(op, "resolve-currentness") == 0 ||
           strcmp(op, "evaluate-decision-apply") == 0 ||
           strcmp(op, "validate-normative-coverage") == 0;
}

static void handle_client(int fd, uid_t candidate_uid) {
    struct ucred cred;
    socklen_t cred_len = sizeof(cred);
    if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &cred_len) != 0 ||
        cred_len != sizeof(cred) || cred.uid != candidate_uid) {
        send_response(fd, "DENY", "PEER_IDENTITY_REJECTED", NULL, NULL);
        return;
    }

    char magic[64], op[96], reference[256], expected_id[512], expected_digest[256];
    char context_len_s[64], boundary_len_s[64], payload_len_s[64];
    if (!recv_line(fd, magic, sizeof(magic)) ||
        !recv_line(fd, op, sizeof(op)) ||
        !recv_line(fd, reference, sizeof(reference)) ||
        !recv_line(fd, expected_id, sizeof(expected_id)) ||
        !recv_line(fd, expected_digest, sizeof(expected_digest)) ||
        !recv_line(fd, context_len_s, sizeof(context_len_s)) ||
        !recv_line(fd, boundary_len_s, sizeof(boundary_len_s)) ||
        !recv_line(fd, payload_len_s, sizeof(payload_len_s))) {
        send_response(fd, "DENY", "IPC_HEADER_MALFORMED", NULL, NULL);
        return;
    }
    if (strcmp(magic, "V24-V6-S7/1") != 0 || !valid_operation(op) ||
        !is_hex64_or_dash(reference) || !is_hex64_or_dash(expected_digest)) {
        send_response(fd, "DENY", "IPC_HEADER_INVALID", NULL, NULL);
        return;
    }

    size_t context_len = 0, boundary_len = 0, payload_len = 0;
    if (!parse_size(context_len_s, &context_len) ||
        !parse_size(boundary_len_s, &boundary_len) ||
        !parse_size(payload_len_s, &payload_len) ||
        context_len == 0 || boundary_len == 0) {
        send_response(fd, "DENY", "IPC_LENGTH_INVALID", NULL, NULL);
        return;
    }

    unsigned char *context = malloc(context_len);
    unsigned char *boundary = malloc(boundary_len);
    unsigned char *payload = payload_len ? malloc(payload_len) : NULL;
    if (!context || !boundary || (payload_len && !payload)) {
        free(context); free(boundary); free(payload);
        send_response(fd, "DENY", "IPC_ALLOCATION_FAILED", NULL, NULL);
        return;
    }
    if (!recv_exact(fd, context, context_len) ||
        !recv_exact(fd, boundary, boundary_len) ||
        (payload_len && !recv_exact(fd, payload, payload_len))) {
        free(context); free(boundary); free(payload);
        send_response(fd, "DENY", "IPC_BODY_TRUNCATED", NULL, NULL);
        return;
    }

    size_t bind_len = context_len + boundary_len + payload_len +
                      strlen(op) + strlen(reference) + strlen(expected_id) + strlen(expected_digest) + 4;
    unsigned char *bind = malloc(bind_len);
    if (!bind) {
        free(context); free(boundary); free(payload);
        send_response(fd, "DENY", "REQUEST_BINDING_FAILED", NULL, NULL);
        return;
    }
    size_t off = 0;
    const char *parts[] = {op, reference, expected_id, expected_digest};
    for (size_t i = 0; i < 4; ++i) {
        size_t n = strlen(parts[i]);
        memcpy(bind + off, parts[i], n); off += n; bind[off++] = '\0';
    }
    memcpy(bind + off, context, context_len); off += context_len;
    memcpy(bind + off, boundary, boundary_len); off += boundary_len;
    if (payload_len) { memcpy(bind + off, payload, payload_len); off += payload_len; }
    char request_digest[65];
    sha256_hex(bind, off, request_digest);
    free(bind);

    char context_path[PATH_MAX], boundary_path[PATH_MAX], payload_path[PATH_MAX] = {0};
    bool ok = materialize_private(context, context_len, "context", context_path) &&
              materialize_private(boundary, boundary_len, "boundary", boundary_path);
    if (ok && payload_len) ok = materialize_private(payload, payload_len, "payload", payload_path);
    free(context); free(boundary); free(payload);
    if (!ok) {
        send_response(fd, "DENY", "TRUSTED_PRIVATE_MATERIALIZATION_FAILED", request_digest, NULL);
        return;
    }

    int st = 0;
    char *gate_output = NULL;
    if (strncmp(op, "resolve-", 8) == 0) {
        char *argv[] = {
            (char *)GATE_PATH, op, context_path, boundary_path, reference,
            expected_id, expected_digest, (char *)GATE_ID, (char *)GATE_VERSION,
            "enforce", NULL
        };
        gate_output = capture_exec(argv, &st);
    } else {
        if (!payload_len) {
            unlink(context_path); unlink(boundary_path);
            send_response(fd, "DENY", "DOWNSTREAM_PAYLOAD_REQUIRED", request_digest, NULL);
            return;
        }
        char *argv[] = {
            (char *)GATE_PATH, op, context_path, boundary_path, payload_path,
            reference, expected_id, expected_digest, (char *)GATE_ID,
            (char *)GATE_VERSION, "enforce", NULL
        };
        gate_output = capture_exec(argv, &st);
    }

    unlink(context_path);
    unlink(boundary_path);
    if (payload_len) unlink(payload_path);

    if (!gate_output) {
        send_response(fd, "DENY", "TRUSTED_GATE_EXECUTION_FAILED", request_digest, NULL);
        return;
    }

    char gate_digest[65];
    sha256_hex((unsigned char *)gate_output, strlen(gate_output), gate_digest);
    bool identity_ok =
        strstr(gate_output, "\"construction_authoritative\":true") != NULL &&
        strstr(gate_output, "\"gate_id\":\"" GATE_ID "\"") != NULL &&
        strstr(gate_output, "\"gate_version\":\"" GATE_VERSION "\"") != NULL;
    bool allow = child_ok(st) && identity_ok &&
                 strstr(gate_output, "\"decision\":\"ALLOW\"") != NULL;

    if (allow) send_response(fd, "ALLOW", "TRUSTED_GATE_ALLOWED", request_digest, gate_digest);
    else send_response(fd, "DENY", "TRUSTED_GATE_REJECTED", request_digest, gate_digest);
    free(gate_output);
}

static int serve(void) {
    if (!prepare_runtime()) {
        fprintf(stderr, "trusted service requires root-owned runtime\n");
        return 2;
    }
    struct passwd *pw = getpwnam(CANDIDATE_USER);
    if (!pw || pw->pw_uid == 0) {
        fprintf(stderr, "candidate identity unresolved or privileged\n");
        return 2;
    }

    unlink(SOCKET_PATH);
    int s = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (s < 0) return 2;
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) != 0) { close(s); return 2; }
    if (chown(SOCKET_PATH, 0, 0) != 0 || chmod(SOCKET_PATH, 0666) != 0 || listen(s, 16) != 0) {
        unlink(SOCKET_PATH); close(s); return 2;
    }

    FILE *pf = fopen(PID_PATH, "w");
    if (!pf) { unlink(SOCKET_PATH); close(s); return 2; }
    fprintf(pf, "%ld\n", (long)getpid());
    fclose(pf);
    if (chown(PID_PATH, 0, 0) != 0 || chmod(PID_PATH, 0444) != 0) {
        unlink(SOCKET_PATH);
        unlink(PID_PATH);
        close(s);
        return 2;
    }

    signal(SIGPIPE, SIG_IGN);
    while (1) {
        int c = accept4(s, NULL, NULL, SOCK_CLOEXEC);
        if (c < 0) { if (errno == EINTR) continue; break; }
        handle_client(c, pw->pw_uid);
        close(c);
    }
    unlink(SOCKET_PATH); unlink(PID_PATH); close(s);
    return 2;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--identity") == 0) {
        printf("{\"authority_effect\":\"%s\",\"service_id\":\"%s\",\"service_version\":\"%s\"}\n",
               AUTHORITY_EFFECT, SERVICE_ID, SERVICE_VERSION);
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "--serve") == 0) return serve();
    fprintf(stderr, "usage: %s --identity|--serve\n", argv[0]);
    return 2;
}
