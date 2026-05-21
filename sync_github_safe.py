#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safer one-click GitHub sync script for:
ocellaris-fish-tracking-yolo-bytetrack

核心改动：
1. 不再使用 git stash / git stash pop，避免 modify/delete 冲突反复出现。
2. 先把本地改动提交成一个普通 commit，再执行 git pull --rebase。
3. 如果远程与本地 commit 仍冲突，Git 会进入 rebase 冲突状态，脚本会停止并给出处理命令。
4. 自动检测 merge/rebase/cherry-pick 冲突状态，避免在仓库不干净时继续同步。
5. 自动显示 unmerged 文件，方便定位冲突。

使用方式：
    python sync_github_safe.py

注意：
- 如果仓库已经处于冲突状态，本脚本不会自动强行处理。
- 先按脚本提示手动解决冲突，再重新运行。
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


# =========================
# 配置区：按需修改
# =========================

REPO_PATH = Path(r"E:\ocellaris-fish-tracking-yolo-bytetrack")
BRANCH = "main"

USE_PROXY = True
PROXY_URL = "http://127.0.0.1:10090"

COMMIT_PREFIX = "Sync local changes"
WAIT_BEFORE_EXIT = True


# =========================
# 工具函数
# =========================

def pause_and_exit(code: int = 0) -> None:
    if WAIT_BEFORE_EXIT:
        try:
            input("\n按 Enter 退出...")
        except EOFError:
            pass
    sys.exit(code)


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
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


def is_git_repo(repo: Path) -> bool:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], repo, check=False)
    return result.returncode == 0 and result.stdout.strip() == "true"


def get_git_dir(repo: Path) -> Path:
    result = run(["git", "rev-parse", "--git-dir"], repo, check=True)
    git_dir_text = result.stdout.strip()
    git_dir = Path(git_dir_text)
    if not git_dir.is_absolute():
        git_dir = repo / git_dir
    return git_dir.resolve()


def has_unmerged_paths(repo: Path) -> bool:
    result = run(["git", "diff", "--name-only", "--diff-filter=U"], repo, check=False)
    if result.stdout.strip():
        print("\n检测到未解决冲突文件：")
        print(result.stdout)
        return True
    return False


def ensure_no_incomplete_git_operation(repo: Path) -> None:
    git_dir = get_git_dir(repo)

    markers = [
        git_dir / "rebase-merge",
        git_dir / "rebase-apply",
        git_dir / "MERGE_HEAD",
        git_dir / "CHERRY_PICK_HEAD",
        git_dir / "REVERT_HEAD",
    ]

    in_operation = any(p.exists() for p in markers)

    if in_operation or has_unmerged_paths(repo):
        print("\n当前仓库处于 merge / rebase / cherry-pick 冲突或未完成状态，脚本已停止。")
        print("\n先查看状态：")
        print("  git status")
        print("\n如果你要保留当前修改，请手动解决冲突后执行：")
        print("  git add <已解决的文件>")
        print("  git rebase --continue        # 如果当前是 rebase")
        print("  git commit                   # 如果当前是 merge")
        print("\n如果你要放弃当前未完成操作，请根据实际情况执行：")
        print("  git rebase --abort")
        print("  git merge --abort")
        print("\n本脚本不会在冲突状态下自动覆盖或删除文件。")
        pause_and_exit(1)


def configure_proxy(repo: Path) -> None:
    if USE_PROXY:
        print(f"\n启用 Git 代理：{PROXY_URL}")
        run(["git", "config", "--global", "http.proxy", PROXY_URL], repo)
        run(["git", "config", "--global", "https.proxy", PROXY_URL], repo)
    else:
        print("\n未启用 Git 代理。")


def get_current_branch(repo: Path) -> str:
    result = run(["git", "branch", "--show-current"], repo, check=True)
    return result.stdout.strip()


def ensure_branch(repo: Path) -> None:
    current = get_current_branch(repo)
    if current != BRANCH:
        print(f"\n当前分支是 {current!r}，切换到 {BRANCH!r}。")
        run(["git", "checkout", BRANCH], repo)
    else:
        print(f"\n当前分支：{BRANCH}")


def has_local_changes(repo: Path) -> bool:
    result = run(["git", "status", "--porcelain"], repo, check=False)
    return bool(result.stdout.strip())


def commit_local_changes_first(repo: Path) -> bool:
    """
    先提交本地改动，替代原来的 stash 逻辑。
    好处：不会再出现 stash pop 把删除/移动文件恢复回来导致 modify/delete 冲突。
    """
    if not has_local_changes(repo):
        print("\n没有检测到本地未提交修改。")
        return False

    print("\n检测到本地未提交修改。")
    print("先提交本地修改，再从 GitHub 拉取远程更新。")

    run(["git", "add", "-A"], repo)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"{COMMIT_PREFIX} {timestamp}"

    result = run(["git", "commit", "-m", commit_msg], repo, check=False)

    if result.returncode != 0:
        output = result.stdout or ""
        if "nothing to commit" in output.lower():
            print("\n没有内容需要提交。")
            return False

        print("\n本地提交失败。请先运行 git status 查看原因。")
        pause_and_exit(result.returncode)

    print("\n本地改动已提交。")
    return True


def pull_rebase(repo: Path) -> None:
    print("\n同步 GitHub 上的最新改动到本地。")
    result = run(["git", "pull", "--rebase", "origin", BRANCH], repo, check=False)

    if result.returncode != 0:
        print("\n拉取远程更新失败，可能发生 rebase 冲突。")
        print("\n请按以下流程处理：")
        print("  1. git status")
        print("  2. 打开冲突文件，手动处理")
        print("  3. git add <已解决文件>")
        print("  4. git rebase --continue")
        print("  5. 重新运行本脚本，或手动执行 git push origin main")
        print("\n如果你想取消这次 rebase：")
        print("  git rebase --abort")
        pause_and_exit(result.returncode)


def push(repo: Path) -> None:
    print("\n推送到 GitHub。")
    result = run(["git", "push", "-u", "origin", BRANCH], repo, check=False)

    if result.returncode != 0:
        print("\n推送失败。常见原因：")
        print("1. 网络或代理连接 GitHub 失败。")
        print("2. GitHub 登录/认证失败。")
        print("3. 远程仓库有新的更新，需要重新运行本脚本。")
        pause_and_exit(result.returncode)


def show_final_status(repo: Path) -> None:
    print("\n最终状态：")
    run(["git", "status", "--short"], repo, check=False)
    run(["git", "log", "-1", "--oneline"], repo, check=False)


def main() -> None:
    print("======================================")
    print(" GitHub Safer One-Click Sync")
    print("======================================")

    repo = REPO_PATH.resolve()
    print(f"\n仓库路径：{repo}")

    if not repo.exists():
        print("\n错误：仓库路径不存在。请修改脚本顶部的 REPO_PATH。")
        pause_and_exit(1)

    if not is_git_repo(repo):
        print("\n错误：该目录不是 Git 仓库。")
        print(f"当前路径：{repo}")
        pause_and_exit(1)

    ensure_no_incomplete_git_operation(repo)
    configure_proxy(repo)
    ensure_branch(repo)

    print("\n拉取远程信息。")
    run(["git", "fetch", "origin", BRANCH], repo)

    # 关键改动：本地改动先提交，不再 stash。
    commit_local_changes_first(repo)

    # 再 rebase 远程更新。
    pull_rebase(repo)

    # pull --rebase 后如果还有工作区变化，说明可能有 hooks 或文件变化，谨慎再次提交。
    if has_local_changes(repo):
        print("\n检测到 rebase 后仍有本地变化，准备再次提交。")
        commit_local_changes_first(repo)

    push(repo)
    show_final_status(repo)

    print("\n======================================")
    print("同步完成。")
    print("本地改动已提交并推送，GitHub 上的更新也已同步回本地。")
    print("======================================")

    pause_and_exit(0)


if __name__ == "__main__":
    main()
