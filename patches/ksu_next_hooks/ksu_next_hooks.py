#!/usr/bin/env python
"""
apply_ksu_hooks.py - Applies KernelSU-Next manual hooks to kernel source files.
Compatible with Python 2.6+ and Python 3.x.

Run from the root of your kernel tree:
    python apply_ksu_hooks.py
"""

from __future__ import print_function
import sys
import os


def read_file(filepath):
    if sys.version_info[0] >= 3:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    else:
        with open(filepath, "rb") as f:
            return f.read().decode("utf-8", errors="replace")


def write_file(filepath, content):
    if sys.version_info[0] >= 3:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(filepath, "wb") as f:
            f.write(content.encode("utf-8"))


def apply_patch(filepath, search, replacement, description):
    if not os.path.isfile(filepath):
        print("[SKIP]    %s: file not found" % filepath)
        return False

    content = read_file(filepath)

    if replacement in content:
        print("[ALREADY] %s: '%s' already applied" % (filepath, description))
        return True

    if search not in content:
        print("[ERROR]   %s: could not find anchor for '%s'" % (filepath, description))
        print("          Searched for:")
        for line in search.splitlines():
            print("              " + line)
        return False

    new_content = content.replace(search, replacement, 1)
    write_file(filepath, new_content)
    print("[OK]      %s: applied '%s'" % (filepath, description))
    return True


patches = [

    # ── fs/exec.c ─────────────────────────────────────────────────────────────

    (
        "fs/exec.c",
        "int do_execve(struct filename *filename,",
        "#ifdef CONFIG_KSU\n"
        "__attribute__((hot))\n"
        "extern int ksu_handle_execveat(int *fd, struct filename **filename_ptr,\n"
        "\t\t\t       void *argv, void *envp, int *flags);\n"
        "#endif\n"
        "\n"
        "int do_execve(struct filename *filename,",
        "exec.c: extern ksu_handle_execveat above do_execve",
    ),

    (
        "fs/exec.c",
        "\tstruct user_arg_ptr argv = { .ptr.native = __argv };\n"
        "\tstruct user_arg_ptr envp = { .ptr.native = __envp };\n"
        "\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n"
        "}",
        "\tstruct user_arg_ptr argv = { .ptr.native = __argv };\n"
        "\tstruct user_arg_ptr envp = { .ptr.native = __envp };\n"
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_execveat((int *)AT_FDCWD, &filename, &argv, &envp, 0);\n"
        "#endif\n"
        "\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n"
        "}",
        "exec.c: ksu_handle_execveat call inside do_execve",
    ),

    (
        "fs/exec.c",
        "\t\t.is_compat = true,\n"
        "\t\t.ptr.compat = __envp,\n"
        "\t};\n"
        "\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n"
        "}",
        "\t\t.is_compat = true,\n"
        "\t\t.ptr.compat = __envp,\n"
        "\t};\n"
        "#ifdef CONFIG_KSU /* 32-bit ksud and 32-on-64 support */\n"
        "\tksu_handle_execveat((int *)AT_FDCWD, &filename, &argv, &envp, 0);\n"
        "#endif\n"
        "\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n"
        "}",
        "exec.c: ksu_handle_execveat call inside compat_do_execve",
    ),

    # ── fs/open.c ─────────────────────────────────────────────────────────────

    (
        "fs/open.c",
        "SYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)",
        "#ifdef CONFIG_KSU\n"
        "__attribute__((hot))\n"
        "extern int ksu_handle_faccessat(int *dfd, const char __user **filename_user,\n"
        "\t\t\t\tint *mode, int *flags);\n"
        "#endif\n"
        "\n"
        "SYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)",
        "open.c: extern ksu_handle_faccessat above SYSCALL_DEFINE3(faccessat)",
    ),

    (
        "fs/open.c",
        "\tif (mode & ~S_IRWXO)\t/* where's F_OK, X_OK, W_OK, R_OK? */",
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_faccessat(&dfd, &filename, &mode, NULL);\n"
        "#endif\n"
        "\n"
        "\tif (mode & ~S_IRWXO)\t/* where's F_OK, X_OK, W_OK, R_OK? */",
        "open.c: ksu_handle_faccessat call inside faccessat",
    ),

    # ── fs/read_write.c ───────────────────────────────────────────────────────

    (
        "fs/read_write.c",
        "SYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)",
        "#ifdef CONFIG_KSU\n"
        "extern bool ksu_vfs_read_hook __read_mostly;\n"
        "extern __attribute__((cold)) int ksu_handle_sys_read(unsigned int fd,\n"
        "\t\t\t\tchar __user **buf_ptr, size_t *count_ptr);\n"
        "#endif\n"
        "\n"
        "SYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)",
        "read_write.c: extern ksu_handle_sys_read above SYSCALL_DEFINE3(read)",
    ),

    (
        "fs/read_write.c",
        "\tif (f.file) {",
        "#ifdef CONFIG_KSU\n"
        "\tif (unlikely(ksu_vfs_read_hook))\n"
        "\t\tksu_handle_sys_read(fd, &buf, &count);\n"
        "#endif\n"
        "\tif (f.file) {",
        "read_write.c: ksu_handle_sys_read call inside read",
    ),

    # ── fs/stat.c ─────────────────────────────────────────────────────────────

    (
        "fs/stat.c",
        "SYSCALL_DEFINE4(newfstatat, int, dfd, const char __user *, filename,",
        "#ifdef CONFIG_KSU\n"
        "__attribute__((hot))\n"
        "extern int ksu_handle_stat(int *dfd, const char __user **filename_user,\n"
        "\t\t\t       int *flags);\n"
        "#endif\n"
        "\n"
        "SYSCALL_DEFINE4(newfstatat, int, dfd, const char __user *, filename,",
        "stat.c: extern ksu_handle_stat above SYSCALL_DEFINE4(newfstatat)",
    ),

    (
        "fs/stat.c",
        "\terror = vfs_fstatat(dfd, filename, &stat, flag);",
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_stat(&dfd, &filename, &flag);\n"
        "#endif\n"
        "\n"
        "\terror = vfs_fstatat(dfd, filename, &stat, flag);",
        "stat.c: ksu_handle_stat call inside newfstatat",
    ),

    # ── kernel/reboot.c ───────────────────────────────────────────────────────

    (
        "kernel/reboot.c",
        "SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd,",
        "#ifdef CONFIG_KSU\n"
        "extern int ksu_handle_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user **arg);\n"
        "#endif\n"
        "\n"
        "SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd,",
        "reboot.c: extern ksu_handle_sys_reboot above SYSCALL_DEFINE4(reboot)",
    ),

    (
        "kernel/reboot.c",
        "\t/* We only trust the superuser with rebooting the system. */",
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_sys_reboot(magic1, magic2, cmd, &arg);\n"
        "#endif\n"
        "\n"
        "\t/* We only trust the superuser with rebooting the system. */",
        "reboot.c: ksu_handle_sys_reboot call inside reboot",
    ),
]


def main():
    ok = True
    for entry in patches:
        filepath, search, replacement, description = entry
        if not apply_patch(filepath, search, replacement, description):
            ok = False

    print("")
    if ok:
        print("All hooks applied successfully.")
        print("Verify with:")
        print("  grep -n ksu_handle fs/exec.c fs/open.c fs/read_write.c fs/stat.c kernel/reboot.c")
    else:
        print("One or more hooks FAILED. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
