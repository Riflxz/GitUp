# core/git_ops.py

import os
import shutil
import tempfile
import re
from pathlib import Path
from typing import Callable
import git
from git import Repo, GitCommandError


def _make_auth_url(repo_url: str, token: str) -> str:
    url = repo_url.strip()
    if not url.endswith(".git"):
        url += ".git"
    url = url.replace("https://", f"https://oauth2:{token}@")
    return url


# ── Clone ─────────────────────────────────────────────────────────

def clone_repo(
    repo_url: str,
    dest_path: str,
    token: str,
    branch: str = "",
    on_progress: Callable[[str], None] | None = None,
) -> None:
    auth_url = _make_auth_url(repo_url, token)
    dest = Path(dest_path)
    dest.mkdir(parents=True, exist_ok=True)

    if on_progress:
        on_progress(f"Memulai clone ke {dest_path}...")

    kwargs = {"url": auth_url, "to_path": str(dest)}
    if branch:
        kwargs["branch"] = branch

    Repo.clone_from(**kwargs)

    if on_progress:
        on_progress("Clone selesai.")


# ── Push Folder ──────────────────────────────────────────────────

def push_folder(
    folder_path: str,
    repo_url: str,
    token: str,
    branch: str,
    commit_message: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    tmp_clone = None
    try:
        auth_url = _make_auth_url(repo_url, token)
        source = Path(folder_path)

        if on_progress:
            on_progress("Meng-clone repository...")

        tmp_clone = tempfile.mkdtemp(prefix="ghuploader_clone_")
        repo = Repo.clone_from(auth_url, tmp_clone)

        if on_progress:
            on_progress(f"Menyiapkan branch '{branch}'...")
        try:
            repo.git.checkout(branch)
        except GitCommandError:
            try:
                repo.git.checkout("-B", branch)
            except GitCommandError:
                dummy = Path(tmp_clone) / ".gitkeep"
                dummy.write_text("")
                repo.git.add(A=True)
                repo.index.commit("init")
                repo.git.checkout("-B", branch)

        dummy_file = Path(tmp_clone) / ".gitkeep"
        if dummy_file.exists():
            dummy_file.unlink()

        if on_progress:
            on_progress("Menyalin file...")

        for item in source.iterdir():
            if item.name == ".git":
                continue
            dst = Path(tmp_clone) / item.name
            if item.is_dir():
                shutil.copytree(str(item), str(dst), dirs_exist_ok=True)
            else:
                shutil.copy2(str(item), str(dst))

        if on_progress:
            on_progress("Menyiapkan file untuk commit...")
        repo.git.add(A=True)

        try:
            has_changes = bool(repo.index.diff("HEAD")) or bool(repo.untracked_files)
        except (ValueError, git.exc.GitCommandError, git.exc.BadName):
            has_changes = bool(repo.index.entries) or bool(repo.untracked_files)

        if not has_changes:
            raise Exception("Tidak ada perubahan baru untuk di-push.")

        if on_progress:
            on_progress(f"Membuat commit: {commit_message}")
        repo.index.commit(commit_message)

        if on_progress:
            on_progress(f"Mengirim ke branch '{branch}'...")
        origin = repo.remote("origin")
        origin.push(refspec=f"HEAD:refs/heads/{branch}")

        if on_progress:
            on_progress("Push berhasil!")

    except GitCommandError as e:
        stderr = str(e.stderr).strip() if e.stderr else ""
        if "rejected" in stderr or "conflict" in stderr or "non-fast-forward" in stderr:
            msg = (
                "Push ditolak karena ada konflik.\n"
                "Remote sudah memiliki commit yang berbeda.\n"
                "Saran: pull terlebih dahulu, lalu coba lagi."
            )
        else:
            msg = f"Gagal push: {stderr or str(e)}"
        raise Exception(msg)
    finally:
        if tmp_clone and os.path.exists(tmp_clone):
            shutil.rmtree(tmp_clone, ignore_errors=True)


# ── Push Files ───────────────────────────────────────────────────

def push_files(
    file_paths: list[str],
    repo_url: str,
    token: str,
    branch: str,
    commit_message: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    tmp_dir = None
    try:
        if on_progress:
            on_progress("Menyiapkan file...")

        tmp_dir = tempfile.mkdtemp(prefix="ghuploader_files_")
        for fp in file_paths:
            src = Path(fp)
            if src.is_file():
                dst = Path(tmp_dir) / src.name
                shutil.copy2(str(src), str(dst))
                if on_progress:
                    on_progress(f"Menyiapkan: {src.name}")

        push_folder(
            folder_path=tmp_dir,
            repo_url=repo_url,
            token=token,
            branch=branch,
            commit_message=commit_message,
            on_progress=on_progress,
        )
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Utils ─────────────────────────────────────────────────────────

def is_git_repo(path: str) -> bool:
    try:
        Repo(path)
        return True
    except git.InvalidGitRepositoryError:
        return False


def get_local_repo_info(path: str) -> dict | None:
    try:
        repo = Repo(path)
        remote_url = ""
        if repo.remotes:
            remote_url = repo.remote("origin").url
            remote_url = re.sub(r"https://[^@]+@", "https://", remote_url)
        return {
            "remote_url":  remote_url,
            "branch":      repo.active_branch.name,
            "has_changes": repo.is_dirty(untracked_files=True),
        }
    except Exception:
        return None
