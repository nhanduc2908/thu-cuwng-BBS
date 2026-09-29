"""Safely commit project source changes and push them to the GitHub upstream."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_ROOT_FILES = {
    ".gitignore",
    "README.md",
    "main.py",
    "requirements.txt",
    "workflow.html",
}
ALLOWED_DIRECTORIES = ("app", "tests", "scripts", ".github")
ALLOWED_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "backups",
    "data",
    "env",
    "reports",
    "uploads",
    "venv",
}


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _is_publishable(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    parts = Path(normalized).parts
    if not parts or any(part in EXCLUDED_DIRECTORY_NAMES for part in parts):
        return False
    if normalized in ALLOWED_ROOT_FILES:
        return True
    if parts[0] not in ALLOWED_DIRECTORIES:
        return False
    path = Path(normalized)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False
    lowered_name = path.name.lower()
    return (
        lowered_name not in {".env", ".env.example"}
        and "secret" not in lowered_name
        and "credential" not in lowered_name
    )


def _publishable_paths(root: Path) -> list[str]:
    tracked = _git(root, "ls-files", "-z")
    if tracked.returncode:
        raise RuntimeError(tracked.stderr.strip() or "Không đọc được danh sách file Git.")
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    if untracked.returncode:
        raise RuntimeError(untracked.stderr.strip() or "Không đọc được file mới.")

    candidates = set(tracked.stdout.split("\0")) | set(untracked.stdout.split("\0"))
    return sorted(
        path
        for path in candidates
        if path and _is_publishable(path) and not (root / path).is_dir()
    )


def update_github(
    commit_message: str,
    project_root: Path = PROJECT_ROOT,
) -> bool:
    """Commit approved source/documentation files and push to the configured GitHub upstream.

    Uses the user's normal Git credential manager; it never handles or stores tokens.
    Returns False when there are no publishable changes.
    """
    root = project_root.resolve()
    inside_worktree = _git(root, "rev-parse", "--is-inside-work-tree")
    if inside_worktree.returncode or inside_worktree.stdout.strip() != "true":
        raise RuntimeError(f"Không tìm thấy Git repository tại: {root}")

    message = commit_message.strip()
    if not message or "\n" in message or "\r" in message:
        raise ValueError("Thông điệp commit phải có nội dung trên một dòng.")

    staged = _git(root, "diff", "--cached", "--quiet")
    if staged.returncode == 1:
        raise RuntimeError(
            "Đang có thay đổi được stage sẵn. Hãy commit hoặc bỏ stage trước khi đồng bộ."
        )
    if staged.returncode != 0:
        raise RuntimeError(staged.stderr.strip() or "Không kiểm tra được trạng thái stage.")

    upstream = _git(
        root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    )
    if upstream.returncode:
        raise RuntimeError(
            "Nhánh hiện tại chưa có upstream. Hãy cấu hình tracking branch trước."
        )
    upstream_name = upstream.stdout.strip()
    remote_name = upstream_name.split("/", 1)[0]
    remote_url = _git(root, "remote", "get-url", remote_name)
    if remote_url.returncode:
        raise RuntimeError(remote_url.stderr.strip() or "Không tìm thấy remote upstream.")
    url = remote_url.stdout.strip().lower()
    if "github.com/" not in url and not url.startswith("git@github.com:"):
        raise RuntimeError("Remote upstream không trỏ tới GitHub; đã dừng để tránh đẩy nhầm.")

    paths = _publishable_paths(root)
    if not paths:
        print("Không tìm thấy file mã nguồn/tài liệu được phép đồng bộ.")
        return False

    add = _git(root, "add", "-A", "--", *paths)
    if add.returncode:
        raise RuntimeError(add.stderr.strip() or "Không stage được file dự án.")
    staged_changes = _git(root, "diff", "--cached", "--quiet")
    if staged_changes.returncode == 0:
        print("Không có thay đổi mã nguồn/tài liệu mới để đồng bộ.")
        return False
    if staged_changes.returncode != 1:
        raise RuntimeError(
            staged_changes.stderr.strip() or "Không kiểm tra được thay đổi đã stage."
        )

    checked = _git(root, "diff", "--cached", "--check")
    if checked.returncode:
        raise RuntimeError(checked.stdout.strip() or checked.stderr.strip())

    commit = _git(
        root,
        "commit",
        "-m",
        message,
        "-m",
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    if commit.returncode:
        raise RuntimeError(commit.stderr.strip() or commit.stdout.strip() or "Commit thất bại.")
    print(commit.stdout.strip())

    push = _git(root, "push")
    if push.returncode:
        raise RuntimeError(
            "Đã tạo commit nhưng push thất bại. Kiểm tra kết nối/quyền GitHub rồi "
            f"thử lại bằng `git push`.\n{push.stderr.strip()}"
        )
    print(push.stderr.strip() or "Đã cập nhật commit lên GitHub.")
    return True


def main(arguments: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Commit project source/documentation and push to GitHub."
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Commit message, for example: Update pet intake workflow",
    )
    options = parser.parse_args(arguments)
    try:
        update_github(options.message)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"GitHub sync failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
