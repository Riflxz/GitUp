import os
import asyncio
import subprocess
import sys
import requests

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.lstrip("vV").split("."))


def get_latest_release(token: str = "") -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(
        "https://api.github.com/repos/Riflxz/GitForge/releases/latest",
        headers=headers,
        timeout=10,
    )
    if resp.status_code == 404:
        resp = requests.get(
            "https://api.github.com/repos/Riflxz/GitForge/releases",
            headers=headers,
            timeout=10,
        )
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
        return {}
    if resp.status_code != 200:
        return {}
    return resp.json()


def check_update(current: str, token: str = "") -> dict:
    release = get_latest_release(token)
    if not release:
        return {"available": False}
    latest_tag = release.get("tag_name", "").lstrip("vV")
    latest_url = release.get("html_url", "")
    if not latest_tag:
        return {"available": False}
    try:
        current_ver = parse_version(current)
        latest_ver = parse_version(latest_tag)
    except (ValueError, TypeError):
        return {"available": False}
    if latest_ver > current_ver:
        return {
            "available": True,
            "latest_tag": release["tag_name"],
            "latest_url": latest_url,
            "current": current,
        }
    return {"available": False}


def is_git_repo(path: str = None) -> bool:
    return os.path.isdir(os.path.join(path or APP_DIR, ".git"))


def apply_update() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Waktu habis saat menarik update."
    except FileNotFoundError:
        return False, "Git tidak ditemukan di sistem."
    except Exception as e:
        return False, str(e)


def install_deps() -> tuple[bool, str]:
    req_file = os.path.join(APP_DIR, "requirements.txt")
    if not os.path.exists(req_file):
        return True, ""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req_file,
             "--break-system-packages"],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Waktu habis saat install dependensi."
    except Exception as e:
        return False, str(e)
