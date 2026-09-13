#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/landlock.h>
#include <linux/prctl.h>
#include <stdio.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_landlock_create_ruleset
#if defined(__x86_64__)
#define SYS_landlock_create_ruleset 444
#define SYS_landlock_add_rule 445
#define SYS_landlock_restrict_self 446
#else
#error "landlock syscall numbers unavailable for this architecture"
#endif
#endif

static int ll_create(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
    return (int)syscall(SYS_landlock_create_ruleset, attr, size, flags);
}

static int ll_restrict(int fd, __u32 flags) {
    return (int)syscall(SYS_landlock_restrict_self, fd, flags);
}

int main(void) {
    int abi = ll_create(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        fprintf(stderr, "R16_LANDLOCK_ABI_UNAVAILABLE errno=%d %s\n", errno, strerror(errno));
        return 2;
    }

    int rootfd = open("/", O_PATH | O_DIRECTORY | O_CLOEXEC);
    if (rootfd < 0) {
        perror("R16_ROOTFD_OPEN_FAILED");
        return 3;
    }
    int dupfd = dup(rootfd);
    if (dupfd < 0) {
        perror("R16_ROOTFD_DUP_FAILED");
        return 4;
    }

    __u64 handled = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR;
    struct landlock_ruleset_attr ruleset = {.handled_access_fs = handled};
    int rs = ll_create(&ruleset, sizeof(ruleset), 0);
    if (rs < 0) {
        fprintf(stderr, "R16_LANDLOCK_RULESET_CREATE_FAILED errno=%d %s abi=%d\n", errno, strerror(errno), abi);
        return 5;
    }
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("R16_NO_NEW_PRIVS_FAILED");
        return 6;
    }
    if (ll_restrict(rs, 0) != 0) {
        fprintf(stderr, "R16_LANDLOCK_RESTRICT_FAILED errno=%d %s abi=%d\n", errno, strerror(errno), abi);
        return 7;
    }
    close(rs);

    errno = 0;
    int direct = open("/proc/self/status", O_RDONLY | O_CLOEXEC);
    int direct_errno = errno;
    if (direct >= 0) close(direct);

    errno = 0;
    int relative = openat(rootfd, "proc/self/status", O_RDONLY | O_CLOEXEC);
    int relative_errno = errno;
    if (relative >= 0) close(relative);

    errno = 0;
    int duplicated = openat(dupfd, "proc/self/status", O_RDONLY | O_CLOEXEC);
    int duplicated_errno = errno;
    if (duplicated >= 0) close(duplicated);

    close(rootfd);
    close(dupfd);

    printf("R16_LANDLOCK_ABI=%d\n", abi);
    printf("R16_DIRECT_PROC_DENIED=%s errno=%d\n", direct < 0 && direct_errno == EACCES ? "PASS" : "FAIL", direct_errno);
    printf("R16_DIRFD_PROC_DENIED=%s errno=%d\n", relative < 0 && relative_errno == EACCES ? "PASS" : "FAIL", relative_errno);
    printf("R16_DUP_DIRFD_PROC_DENIED=%s errno=%d\n", duplicated < 0 && duplicated_errno == EACCES ? "PASS" : "FAIL", duplicated_errno);

    if (!(direct < 0 && direct_errno == EACCES)) return 11;
    if (!(relative < 0 && relative_errno == EACCES)) return 12;
    if (!(duplicated < 0 && duplicated_errno == EACCES)) return 13;
    return 0;
}
