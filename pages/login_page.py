# pages/login_page.py

import asyncio
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    DANGER, TEXT_MAIN, TEXT_MUTED, ACCENT,
    PAGE_DASHBOARD
)
from core import auth
from core.state import AppState


def login_page(page: ft.Page, state: AppState, navigate: callable) -> ft.Container:

    token_input = ft.TextField(
        hint_text="ghp_xxxxxxxxxxxxxxxxxxxx",
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        password=True,
        can_reveal_password=True,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        cursor_color=TEXT_MAIN,
        width=360,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )

    error_text = ft.Text("", color=DANGER, size=13, visible=False)
    loading    = ft.ProgressRing(width=20, height=20, color=PRIMARY,
                                 visible=False)
    login_btn  = ft.ElevatedButton(
        "Masuk",
        width=360,
        bgcolor=PRIMARY,
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(vertical=14),
        ),
    )

    def set_loading(active: bool):
        loading.visible   = active
        login_btn.disabled = active
        login_btn.text    = "Memeriksa..." if active else "Masuk"
        page.update()

    async def _auto_login(token: str):
        if not token:
            return
        set_loading(True)
        try:
            ok, info = await asyncio.to_thread(auth.validate_token, token)
            if ok:
                auth.save_token(token)
                state.token        = token
                state.username     = info["login"]
                state.avatar_url   = info["avatar_url"]
                state.user_display = info["name"]
                navigate(PAGE_DASHBOARD)
            else:
                set_loading(False)
        except Exception:
            set_loading(False)

    async def do_login(_):
        token = token_input.value.strip()
        error_text.visible = False

        if not token:
            error_text.value   = "Token tidak boleh kosong."
            error_text.visible = True
            page.update()
            return

        set_loading(True)

        try:
            ok, info = await asyncio.to_thread(auth.validate_token, token)
            if ok:
                auth.save_token(token)
                state.token        = token
                state.username     = info["login"]
                state.avatar_url   = info["avatar_url"]
                state.user_display = info["name"]
                set_loading(False)
                navigate(PAGE_DASHBOARD)
            else:
                set_loading(False)
                error_text.value   = info.get("error", "Token tidak valid.")
                error_text.visible = True
                page.update()
        except Exception as e:
            set_loading(False)
            error_text.value   = str(e)
            error_text.visible = True
            page.update()

    def _show_token_guide():
        guide_dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Cara Mendapatkan Token", color=TEXT_MAIN,
                          weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [
                        ft.Text(
                            "1. Buka halaman GitHub Token\n"
                            "   (tombol 'Buka Halaman Token' di bawah)\n\n"
                            "2. Klik 'Generate new token' lalu\n"
                            "   pilih 'Generate new token (classic)'\n\n"
                            "3. Beri nama token (contoh: GitForge)\n\n"
                            "4. Centang scope berikut:\n"
                            "   • repo (akses penuh ke repository)\n"
                            "   • delete_repo (hapus repository)\n\n"
                            "5. Klik 'Generate token' di bawah\n\n"
                            "6. Salin token yang muncul\n"
                            "   (token hanya muncul sekali!)\n\n"
                            "7. Tempel token di kolom di atas,\n"
                            "   lalu klik 'Masuk'",
                            color=TEXT_MAIN, size=13,
                        ),
                    ],
                    spacing=12, tight=True,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Tutup",
                    style=ft.ButtonStyle(color=TEXT_MUTED),
                    on_click=lambda _: _close_guide(guide_dialog),
                ),
                ft.ElevatedButton(
                    "Buka Halaman Token",
                    bgcolor=PRIMARY, color="#FFFFFF",
                    url="https://github.com/settings/tokens/new",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(guide_dialog)
        guide_dialog.open = True
        page.update()

    def _close_guide(dialog: ft.AlertDialog):
        dialog.open = False
        page.update()

    login_btn.on_click = do_login

    saved = auth.load_token()
    if saved:
        token_input.value = saved
        page.run_task(_auto_login, saved)

    return ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                ft.Image(src="logo.png", width=80, height=80, fit=ft.ImageFit.CONTAIN),
                ft.Text(
                    "GitForge",
                    size=26, color=TEXT_MAIN,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Masuk dengan Personal Access Token",
                    size=14, color=TEXT_MUTED,
                ),
                ft.Container(height=16),
                token_input,
                ft.Container(height=4),
                ft.TextButton(
                    "Cara mendapatkan token →",
                    style=ft.ButtonStyle(color=ACCENT),
                    on_click=lambda _: _show_token_guide(),
                ),
                ft.Container(height=8),
                login_btn,
                ft.Container(height=4),
                ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                error_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            tight=True,
        ),
    )
