# components/dialogs.py

import flet as ft
from config import (
    BG_SURFACE, BG_INPUT, BORDER, PRIMARY, DANGER,
    TEXT_MAIN, TEXT_MUTED, ACCENT
)


def show_error(page: ft.Page, judul: str, pesan: str) -> None:
    def close(_):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text(judul, color=DANGER, weight=ft.FontWeight.BOLD),
        content=ft.Text(pesan, color=TEXT_MAIN),
        actions=[
            ft.TextButton("Tutup", on_click=close,
                          style=ft.ButtonStyle(color=TEXT_MUTED)),
        ],
        bgcolor=BG_SURFACE,
        shape=ft.RoundedRectangleBorder(radius=8),
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_success(page: ft.Page, judul: str, pesan: str,
                 on_close: callable = None) -> None:
    def close(_):
        dialog.open = False
        page.update()
        if on_close:
            on_close()

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text(judul, color=PRIMARY, weight=ft.FontWeight.BOLD),
        content=ft.Text(pesan, color=TEXT_MAIN),
        actions=[
            ft.ElevatedButton(
                "OK", on_click=close,
                bgcolor=PRIMARY, color="#FFFFFF",
            ),
        ],
        bgcolor=BG_SURFACE,
        shape=ft.RoundedRectangleBorder(radius=8),
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_confirm(page: ft.Page, judul: str, pesan: str,
                 on_confirm: callable) -> None:
    def confirm(_):
        dialog.open = False
        page.update()
        on_confirm()

    def cancel(_):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text(judul, color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
        content=ft.Text(pesan, color=TEXT_MUTED),
        actions=[
            ft.TextButton("Batal", on_click=cancel,
                          style=ft.ButtonStyle(color=TEXT_MUTED)),
            ft.ElevatedButton(
                "Ya, Lanjutkan", on_click=confirm,
                bgcolor=DANGER, color="#FFFFFF",
            ),
        ],
        bgcolor=BG_SURFACE,
        shape=ft.RoundedRectangleBorder(radius=8),
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


class ProgressDialog:
    def __init__(self, page: ft.Page, judul: str):
        self.page = page
        self._log_text = ft.Text(
            "Memulai...",
            color=TEXT_MUTED,
            size=12,
            selectable=True,
        )
        self._progress = ft.ProgressBar(
            color=PRIMARY,
            bgcolor=BORDER,
            width=400,
        )
        self._dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text(judul, color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [
                        self._progress,
                        ft.Container(height=8),
                        ft.Container(
                            content=self._log_text,
                            bgcolor=BG_INPUT,
                            border_radius=6,
                            padding=ft.padding.all(10),
                            width=420,
                        ),
                    ],
                    tight=True,
                ),
            ),
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )

    def show(self) -> None:
        self.page.overlay.append(self._dialog)
        self._dialog.open = True
        self.page.update()

    def log(self, msg: str) -> None:
        self._log_text.value = msg
        try:
            self.page.update()
        except Exception:
            pass

    def close(self) -> None:
        self._dialog.open = False
        try:
            self.page.update()
        except Exception:
            pass
