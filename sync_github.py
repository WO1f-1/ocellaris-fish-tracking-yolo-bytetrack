#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-click GitHub sync script for:
ocellaris-fish-tracking-yolo-bytetrack

功能：
1. 自动进入指定仓库目录
2. 自动设置 GitHub 代理端口，可按需关闭
3. 自动拉取 GitHub 远程更新
4. 自动保留本地未提交修改
5. 自动提交本地新增、修改、删除的文件
6. 自动推送到 GitHub

使用方式：
1. 把本文件放在任意位置，或放在仓库根目录。
2. 确认 REPO_PATH 是你的本地仓库路径。
3. 双击运行，或在终端运行：
   python sync_github.py

注意：
- 电脑必须已安装 Git。
- 如果 GitHub 认证弹窗出现，请按提示登录。
- 如果本地和 GitHub 同时修改了同一个文件的同一处内容，可能需要手动解决冲突。
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# =========================
# 配置区：按需修改
# =========================

# 你的本地仓库路径
REPO_PATH = Path(r"E:\ocellaris-fish-tracking-yolo-bytetrack")

# 远程分支
BRANCH = "main"

# 是否启用 Git 代理
USE_PROXY = True

# 你的代理端口。你之前查到的是 10090
PROXY_URL = "http://127.0.0.1:10090"

# 自动提交信息前缀
COMMIT_PREFIX = "Sync local changes"

# 是否在脚本结束后等待按 Enter，适合双击运行时查看结果
WAIT_BEFORE_EXIT = True


# =========================
# 工具函数
# =========================

def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令并实时显示输出。"""
    print(f"\n$ {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        print("\n错误：找不到 Git。请先安装 Git for Windows，然后重试。")
        pause_and_exit(1)

    if result.stdout:
        print(result.stdout)

    if check and result.returncode != 0:
        print(f"\n命令执行失败，退出码：{result.returncode}")
        pause_and_exit(result.returncode)

    return result


def pause_and_exit(code: int = 0) -> None:
    if WAIT_BEFORE_EXIT:
        try:
            input("\n按 Enter 退出...")
        except EOFError:
            pass
    sys.exit(code)


def has_local_changes(repo: Path) -> bool:
    """检测是否有未提交的新增、修改或删除。"""
    result = run(["git", "status", "--porcelain"], repo, check=False)
    return bool(result.stdout.strip())


def is_git_repo(repo: Path) -> bool:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], repo, check=False)
    return result.returncode == 0 and result.stdout.strip() == "true"


def ensure_clean_rebase_state(repo: Path) -> None:
    """避免在 rebase/merge 中间继续自动同步。"""
    git_dir_result = run(["git", "rev-parse", "--git-dir"], repo, check=False)
    if git_dir_result.returncode != 0:
        return

    git_dir = (repo / git_dir_result.stdout.strip()).resolve()
    rebase_merge = git_dir / "rebase-merge"
    rebase_apply = git_dir / "rebase-apply"
    merge_head = git_dir / "MERGE_HEAD"

    if rebase_merge.exists() or rebase_apply.exists() or merge_head.exists():
        print("\n检测到当前仓库正处于 rebase 或 merge 未完成状态。")
        print("请先手动解决冲突，或执行以下命令取消：")
        print("  git rebase --abort")
        print("或：")
        print("  git merge --abort")
        pause_and_exit(1)


def configure_proxy(repo: Path) -> None:
    if USE_PROXY:
        print(f"\n启用 Git 代理：{PROXY_URL}")
        run(["git", "config", "--global", "http.proxy", PROXY_URL], repo)
        run(["git", "config", "--global", "https.proxy", PROXY_URL], repo)
    else:
        print("\n未启用 Git 代理。")


def get_current_branch(repo: Path) -> str:
    result = run(["git", "branch", "--show-current"], repo)
    return result.stdout.strip()


def ensure_branch(repo: Path) -> None:
    current = get_current_branch(repo)
    if current != BRANCH:
        print(f"\n当前分支是 {current!r}，切换到 {BRANCH!r}。")
        run(["git", "checkout", BRANCH], repo)
    else:
        print(f"\n当前分支：{BRANCH}")


def stash_local_changes(repo: Path) -> bool:
    if has_local_changes(repo):
        print("\n检测到本地未提交修改，临时保存到 stash。")
        run(["git", "stash", "push", "-u", "-m", "auto-stash-before-python-sync"], repo)
        return True

    print("\n没有检测到本地未提交修改。")
    return False


def pop_stash(repo: Path) -> None:
    print("\n恢复刚才临时保存的本地修改。")
    result = run(["git", "stash", "pop"], repo, check=False)
    if result.returncode != 0:
        print("\n恢复 stash 时发生冲突。")
        print("请打开冲突文件，手动处理 <<<<<<<、=======、>>>>>>> 标记。")
        print("处理完成后执行：")
        print("  git add .")
        print("  git commit -m \"Resolve sync conflicts\"")
        print("  git push origin main")
        pause_and_exit(result.returncode)


def commit_local_changes(repo: Path) -> bool:
    if not has_local_changes(repo):
        print("\n没有新的本地改动需要提交。")
        return False

    print("\n提交本地改动。")
    run(["git", "add", "-A"], repo)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"{COMMIT_PREFIX} {timestamp}"

    result = run(["git", "commit", "-m", commit_msg], repo, check=False)
    if result.returncode != 0:
        output = result.stdout or ""
        if "nothing to commit" in output.lower():
            print("\n没有内容需要提交。")
            return False
        print("\n提交失败。")
        pause_and_exit(result.returncode)

    return True


def main() -> None:
    print("======================================")
    print(" GitHub One-Click Sync")
    print("======================================")

    repo = REPO_PATH.resolve()

    print(f"\n仓库路径：{repo}")

    if not repo.exists():
        print("\n错误：仓库路径不存在。请修改脚本顶部的 REPO_PATH。")
        pause_and_exit(1)

    if not is_git_repo(repo):
        print("\n错误：该目录不是 Git 仓库。")
        print("请确认路径是：E:\\ocellaris-fish-tracking-yolo-bytetrack")
        pause_and_exit(1)

    ensure_clean_rebase_state(repo)
    configure_proxy(repo)
    ensure_branch(repo)

    print("\n拉取远程信息。")
    run(["git", "fetch", "origin", BRANCH], repo)

    stashed = stash_local_changes(repo)

    print("\n同步 GitHub 上的最新改动到本地。")
    pull_result = run(["git", "pull", "--rebase", "origin", BRANCH], repo, check=False)
    if pull_result.returncode != 0:
        print("\n拉取远程更新失败。可能存在冲突或网络问题。")
        print("如果看到 CONFLICT，请手动解决冲突后执行：")
        print("  git add .")
        print("  git rebase --continue")
        pause_and_exit(pull_result.returncode)

    if stashed:
        pop_stash(repo)

    commit_local_changes(repo)

    print("\n推送到 GitHub。")
    push_result = run(["git", "push", "-u", "origin", BRANCH], repo, check=False)
    if push_result.returncode != 0:
        print("\n推送失败。常见原因：")
        print("1. 网络或代理连接 GitHub 失败。")
        print("2. GitHub 登录/认证失败。")
        print("3. 远程仓库有新的更新，需要重新运行本脚本。")
        pause_and_exit(push_result.returncode)

    print("\n======================================")
    print("同步完成。")
    print("本地文件已提交并推送到 GitHub，GitHub 上的改动也已同步回本地。")
    print("======================================")

    pause_and_exit(0)


if __name__ == "__main__":
    main()
