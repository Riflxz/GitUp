# main.py

import base64
import flet as ft
from config import (
    APP_NAME, WIN_WIDTH, WIN_HEIGHT, BG_MAIN,
    PAGE_LOGIN, PAGE_DASHBOARD, PAGE_CREATE,
    PAGE_UPLOAD, PAGE_CLONE, PAGE_BRANCHES, PAGE_EDIT, PAGE_INFO
)
from core.state import AppState


def main(page: ft.Page) -> None:
    page.title          = APP_NAME
    page.window.width   = WIN_WIDTH
    page.window.height  = WIN_HEIGHT
    page.window.min_width  = 800
    page.window.min_height = 600
    page.theme_mode     = ft.ThemeMode.DARK
    page.bgcolor        = BG_MAIN
    page.padding        = 0
    page.spacing        = 0
    page.fonts          = {}

    with open("icon.png", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    page.window.icon = f"data:image/png;base64,{b64}"
    page.update()

    state = AppState()

    def navigate(destination: str) -> None:
        state.current_page = destination
        page.controls.clear()
        page.overlay.clear()

        if destination == PAGE_LOGIN:
            from pages.login_page import login_page
            page.controls.append(
                login_page(page, state, navigate)
            )

        elif destination == PAGE_DASHBOARD:
            from pages.dashboard_page import dashboard_page
            page.controls.append(
                dashboard_page(page, state, navigate)
            )

        elif destination == PAGE_CREATE:
            from pages.create_repo_page import create_repo_page
            page.controls.append(
                create_repo_page(page, state, navigate)
            )

        elif destination == PAGE_UPLOAD:
            from pages.upload_page import upload_page
            page.controls.append(
                upload_page(page, state, navigate)
            )

        elif destination == PAGE_CLONE:
            from pages.clone_page import clone_page
            page.controls.append(
                clone_page(page, state, navigate)
            )

        elif destination == PAGE_BRANCHES:
            from pages.branch_page import branch_page
            page.controls.append(
                branch_page(page, state, navigate)
            )

        elif destination == PAGE_EDIT:
            from pages.edit_repo_page import edit_repo_page
            page.controls.append(
                edit_repo_page(page, state, navigate)
            )

        elif destination == PAGE_INFO:
            from pages.info_page import info_page
            page.controls.append(
                info_page(page, state, navigate)
            )

        else:
            page.controls.append(
                ft.Container(
                    expand=True,
                    bgcolor=BG_MAIN,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        f"Halaman '{destination}' tidak ditemukan.",
                        color="#8B949E",
                        size=16,
                    ),
                )
            )

        page.update()

    navigate(PAGE_LOGIN)


if __name__ == "__main__":
    ft.app(target=main)
