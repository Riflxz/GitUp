# pages/dashboard_page.py

import asyncio
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, ACCENT, DANGER,
    PAGE_CREATE, PAGE_UPLOAD, PAGE_CLONE, PAGE_BRANCHES, PAGE_EDIT, PAGE_INFO
)
from core import github_api
from core.state import AppState
from components.sidebar import Sidebar
from components.repo_card import RepoCard
from components import dialogs


def dashboard_page(page: ft.Page, state: AppState, navigate: callable) -> ft.Row:

    all_repos      = []
    filtered_repos = []
    search_val     = ""
    filter_val     = "semua"
    sort_val       = "terbaru"

    repo_grid = ft.Column(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    loading_indicator = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(color=PRIMARY),
                ft.Text("Memuat repository...", color=TEXT_MUTED, size=13),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.alignment.center,
        expand=True,
        visible=False,
    )

    empty_state = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.INBOX_OUTLINED, size=52, color=TEXT_MUTED),
                ft.Text("Tidak ada repository ditemukan",
                        color=TEXT_MUTED, size=14),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        expand=True,
        visible=False,
    )

    def _apply_filter_sort():
        nonlocal filtered_repos
        result = list(all_repos)

        if filter_val == "publik":
            result = [r for r in result if not r["private"]]
        elif filter_val == "privat":
            result = [r for r in result if r["private"]]

        if search_val:
            q = search_val.lower()
            result = [r for r in result
                      if q in r["name"].lower()
                      or q in r.get("description", "").lower()]

        if sort_val == "nama_az":
            result.sort(key=lambda r: r["name"].lower())
        elif sort_val == "nama_za":
            result.sort(key=lambda r: r["name"].lower(), reverse=True)

        filtered_repos = result

    def _render_repos():
        repo_grid.controls.clear()

        if not filtered_repos:
            empty_state.visible  = True
            repo_grid.visible    = False
        else:
            empty_state.visible  = False
            repo_grid.visible    = True

            for i in range(0, len(filtered_repos), 3):
                chunk = filtered_repos[i:i + 3]
                row = ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=RepoCard(
                                repo=r,
                                on_upload=lambda repo: _go_action(repo, PAGE_UPLOAD),
                                on_clone=lambda repo: _go_action(repo, PAGE_CLONE),
                                on_branches=lambda repo: _go_action(repo, PAGE_BRANCHES),
                                on_delete=lambda repo: _confirm_delete(repo),
                                on_settings=lambda repo: _go_action(repo, PAGE_EDIT),
                                on_info=lambda repo: _go_action(repo, PAGE_INFO),
                            ),
                        )
                        for r in chunk
                    ],
                )
                repo_grid.controls.append(row)

        page.update()

    def _go_action(repo: dict, destination: str):
        state.selected_repo = repo
        navigate(destination)

    def _confirm_delete(repo: dict):
        dialogs.show_confirm(
            page,
            judul=f"Hapus '{repo['name']}'?",
            pesan=(
                "Repository ini akan DIHAPUS PERMANEN dari GitHub.\n"
                "Tindakan ini tidak dapat dibatalkan."
            ),
            on_confirm=lambda: page.run_task(_do_delete, repo),
        )

    async def _do_delete(repo: dict):
        try:
            await asyncio.to_thread(
                github_api.delete_repo, state.token, repo["full_name"])
            await _load_repos()
        except Exception as e:
            dialogs.show_error(page, "Gagal Menghapus", str(e))

    async def _load_repos():
        nonlocal all_repos
        loading_indicator.visible = True
        repo_grid.visible         = False
        empty_state.visible       = False
        page.update()

        try:
            all_repos = await asyncio.to_thread(
                github_api.get_repos, state.token)
        except Exception as e:
            all_repos = []
            dialogs.show_error(page, "Gagal Memuat", str(e))
        finally:
            loading_indicator.visible = False
            _apply_filter_sort()
            _render_repos()
            if state.pending_success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.CHECK_CIRCLE, color="#FFFFFF", size=18),
                            ft.Text(state.pending_success, color="#FFFFFF", size=14),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#238636",
                    behavior=ft.SnackBarBehavior.FLOATING,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    duration=4000,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                )
                page.snack_bar.open = True
                state.pending_success = None
                page.update()

    def on_search(e):
        nonlocal search_val
        search_val = e.control.value
        _apply_filter_sort()
        _render_repos()

    filter_dd = ft.Dropdown(
        value="semua",
        width=130,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        options=[
            ft.dropdown.Option("semua",  "Semua"),
            ft.dropdown.Option("publik", "Publik"),
            ft.dropdown.Option("privat", "Privat"),
        ],
        on_change=lambda e: _set_filter(e.control.value),
    )

    sort_dd = ft.Dropdown(
        value="terbaru",
        width=160,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        options=[
            ft.dropdown.Option("terbaru", "Terbaru diupdate"),
            ft.dropdown.Option("nama_az", "Nama A → Z"),
            ft.dropdown.Option("nama_za", "Nama Z → A"),
        ],
        on_change=lambda e: _set_sort(e.control.value),
    )

    def _set_filter(val):
        nonlocal filter_val
        filter_val = val
        _apply_filter_sort()
        _render_repos()

    def _set_sort(val):
        nonlocal sort_val
        sort_val = val
        _apply_filter_sort()
        _render_repos()

    def do_logout():
        from core.auth import delete_token
        from config import PAGE_LOGIN
        delete_token()
        state.token    = ""
        state.username = ""
        navigate(PAGE_LOGIN)

    sidebar = Sidebar(
        username=state.username,
        current_page="dashboard",
        on_navigate=navigate,
        on_logout=do_logout,
        avatar_url=state.avatar_url,
    )

    header = ft.Container(
        bgcolor=BG_SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        content=ft.Row(
            [
                ft.Text(
                    f"Halo, {state.username}!",
                    size=18, color=TEXT_MAIN,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Buat Repository",
                    icon=ft.icons.ADD,
                    bgcolor=PRIMARY,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda _: navigate(PAGE_CREATE),
                ),
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    icon_color=TEXT_MUTED,
                    tooltip="Refresh",
                    on_click=lambda _: page.run_task(_load_repos),
                ),
            ],
        ),
    )

    toolbar = ft.Container(
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        content=ft.Row(
            [
                ft.TextField(
                    hint_text="Cari repository...",
                    hint_style=ft.TextStyle(color=TEXT_MUTED),
                    bgcolor=BG_INPUT,
                    border_color=BORDER,
                    focused_border_color=PRIMARY,
                    color=TEXT_MAIN,
                    cursor_color=TEXT_MAIN,
                    expand=True,
                    border_radius=8,
                    content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    on_change=on_search,
                ),
                filter_dd,
                sort_dd,
            ],
            spacing=10,
        ),
    )

    content_area = ft.Container(
        expand=True,
        padding=ft.padding.all(16),
        content=ft.Stack(
            [
                repo_grid,
                loading_indicator,
                empty_state,
            ],
            expand=True,
        ),
    )

    main_content = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        content=ft.Column(
            [header, toolbar, content_area],
            spacing=0,
            expand=True,
        ),
    )

    page.run_task(_load_repos)

    return ft.Row(
        [sidebar, main_content],
        spacing=0,
        expand=True,
    )
