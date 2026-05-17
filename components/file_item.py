# components/file_item.py

import os
import flet as ft
from config import BG_INPUT, BORDER, TEXT_MAIN, TEXT_MUTED, DANGER


def _file_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    icons_map = {
        ".py":   ft.icons.CODE,
        ".js":   ft.icons.CODE,
        ".ts":   ft.icons.CODE,
        ".html": ft.icons.WEB,
        ".css":  ft.icons.PALETTE,
        ".md":   ft.icons.DESCRIPTION,
        ".txt":  ft.icons.ARTICLE,
        ".json": ft.icons.DATA_OBJECT,
        ".yaml": ft.icons.SETTINGS,
        ".yml":  ft.icons.SETTINGS,
        ".png":  ft.icons.IMAGE,
        ".jpg":  ft.icons.IMAGE,
        ".jpeg": ft.icons.IMAGE,
        ".pdf":  ft.icons.PICTURE_AS_PDF,
        ".zip":  ft.icons.FOLDER_ZIP,
    }
    return icons_map.get(ext, ft.icons.INSERT_DRIVE_FILE_OUTLINED)


def _human_size(path: str) -> str:
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/1024/1024:.1f} MB"
    except Exception:
        return "?"


class FileItem(ft.UserControl):
    def __init__(self, path: str, on_remove: callable):
        super().__init__()
        self.path = path
        self.on_remove = on_remove

    def build(self):
        filename = os.path.basename(self.path)
        return ft.Container(
            bgcolor=BG_INPUT,
            border_radius=6,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row(
                [
                    ft.Icon(_file_icon(filename), size=16, color=TEXT_MUTED),
                    ft.Column(
                        [
                            ft.Text(filename, size=13, color=TEXT_MAIN,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(self.path, size=10, color=TEXT_MUTED,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=1,
                        tight=True,
                        expand=True,
                    ),
                    ft.Text(_human_size(self.path), size=11, color=TEXT_MUTED),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_size=16,
                        icon_color=DANGER,
                        tooltip="Hapus dari list",
                        on_click=lambda _: self.on_remove(self.path),
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(4),
                        ),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
