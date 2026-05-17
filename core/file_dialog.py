# core/file_dialog.py — Fallback file/folder picker via tkinter + clipboard paste

import os
import re
import threading
import subprocess


def pick_folder(title: str = "Pilih Folder") -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()

    folder = filedialog.askdirectory(title=title)
    root.destroy()

    return folder if folder else ""


def pick_file(title: str = "Pilih File") -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()

    path = filedialog.askopenfilename(title=title)
    root.destroy()

    return path if path else ""


def pick_files(title: str = "Pilih File") -> list[str]:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()

    files = filedialog.askopenfilenames(title=title)
    root.destroy()

    return list(files) if files else []


def pick_folder_async(on_result: callable, title: str = "Pilih Folder"):
    def _run():
        try:
            folder = pick_folder(title)
            on_result(folder)
        except Exception:
            on_result("")

    threading.Thread(target=_run, daemon=True).start()


def pick_files_async(on_result: callable, title: str = "Pilih File"):
    def _run():
        try:
            files = pick_files(title)
            on_result(files)
        except Exception:
            on_result([])

    threading.Thread(target=_run, daemon=True).start()


def paste_file_paths() -> list[str]:
    """
    Baca file paths dari clipboard.
    Support: Copied files dari file manager (Nautilus, Dolphin, Thunar, dll).
    Format: file:///path/to/file (URI list) atau path langsung.
    """
    paths = []

    # Coba xclip (X11)
    try:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o", "-t", "text/uri-list"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            paths = _parse_uri_list(result.stdout.strip())
            if paths:
                return paths
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Coba xclip tanpa tipe (fallback)
    try:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            paths = _parse_uri_list(result.stdout.strip())
            if paths:
                return paths
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Coba wl-paste (Wayland)
    try:
        result = subprocess.run(
            ["wl-paste"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            paths = _parse_uri_list(result.stdout.strip())
            if paths:
                return paths
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Fallback: tkinter clipboard
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        raw = root.clipboard_get()
        root.destroy()
        paths = _parse_uri_list(raw)
        if paths:
            return paths
    except Exception:
        pass

    return []


def _parse_uri_list(text: str) -> list[str]:
    """Parse URI list format atau plain paths."""
    paths = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # file:/// URI
        if line.startswith("file://"):
            path = line[7:]
            path = _url_decode(path)
            if path and os.path.exists(path):
                paths.append(path)

        # Plain path
        elif os.path.exists(line):
            paths.append(line)

        # Coba parse sebagai path dengan leading/trailing quotes
        else:
            clean = line.strip("\"'")
            if clean != line and os.path.exists(clean):
                paths.append(clean)

    return paths


def _url_decode(url: str) -> str:
    """Decode URL-encoded characters dalam path."""
    try:
        from urllib.parse import unquote
        return unquote(url)
    except Exception:
        return url
