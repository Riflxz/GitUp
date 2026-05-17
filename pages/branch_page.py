# pages/branch_page.py

import asyncio
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, DANGER, ACCENT,
    PAGE_DASHBOARD
)
from core import github_api
from core.state import AppState
from components.sidebar import Sidebar
from components import dialogs


def branch_page(page: ft.Page, state: AppState,
                navigate: callable) -> ft.Row:

    repo = state.selected_repo
    if not repo:
        navigate(PAGE_DASHBOARD)
        return ft.Row()

    default_branch = repo.get("default_branch", "main")
    branches_list  = []

    branch_col     = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    loading_ring   = ft.ProgressRing(color=PRIMARY, visible=True)

    def _render_branches():
        branch_col.controls.clear()
        for b in branches_list:
            is_default = (b == default_branch)
            branch_col.controls.append(
                ft.Container(
                    bgcolor=BG_SURFACE,
                    border=ft.border.all(1, BORDER),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.ACCOUNT_TREE_OUTLINED,
                                    size=16, color=ACCENT),
                            ft.Text(b, size=14, color=TEXT_MAIN,
                                    expand=True),
                            ft.Container(
                                content=ft.Text("Default", size=11,
                                                color="#FFFFFF"),
                                bgcolor=PRIMARY,
                                border_radius=20,
                                padding=ft.padding.symmetric(
                                    horizontal=8, vertical=2),
                                visible=is_default,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=DANGER if not is_default
                                           else TEXT_MUTED,
                                tooltip="Hapus branch" if not is_default
                                        else "Branch default tidak bisa dihapus",
                                disabled=is_default,
                                on_click=(lambda _, branch=b:
                                          _confirm_delete(branch))
                                          if not is_default else None,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        loading_ring.visible = False
        page.update()

    async def _load_branches():
        nonlocal branches_list
        try:
            branches_list = await asyncio.to_thread(
                github_api.get_branches, state.token, repo["full_name"])
            _render_branches()
        except Exception as e:
            loading_ring.visible = False
            page.update()
            dialogs.show_error(page, "Gagal Memuat Branch", str(e))

    page.run_task(_load_branches)

    def _confirm_delete(branch: str):
        dialogs.show_confirm(
            page,
            f"Hapus Branch '{branch}'?",
            "Branch ini akan dihapus permanen dari GitHub.",
            on_confirm=lambda: page.run_task(_do_delete, branch),
        )

    async def _do_delete(branch: str):
        try:
            await asyncio.to_thread(
                github_api.delete_branch, state.token, repo["full_name"], branch)
            branches_list.remove(branch)
            _render_branches()
        except Exception as e:
            dialogs.show_error(page, "Gagal Menghapus Branch", str(e))

    def _open_create_dialog(_):
        new_name_input = ft.TextField(
            label="Nama branch baru",
            hint_text="contoh: feature/fitur-baru",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
        )

        from_dd = ft.Dropdown(
            label="Dari branch",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
            options=[ft.dropdown.Option(b, b) for b in branches_list],
            value=default_branch,
        )

        async def _do_create(_):
            new_name = new_name_input.value.strip()
            from_b   = from_dd.value

            if not new_name:
                return
            if new_name in branches_list:
                dialogs.show_error(page, "Branch Sudah Ada",
                                   f"Branch '{new_name}' sudah ada.")
                return

            create_dialog.open = False
            page.update()

            try:
                await asyncio.to_thread(
                    github_api.create_branch,
                    state.token, repo["full_name"],
                    new_name, from_b)
                branches_list.append(new_name)
                _render_branches()
                dialogs.show_success(
                    page, "Branch Dibuat!",
                    f"Branch '{new_name}' berhasil dibuat dari '{from_b}'.",
                )
            except Exception as e:
                dialogs.show_error(page, "Gagal Membuat Branch", str(e))

        def _cancel(_):
            create_dialog.open = False
            page.update()

        create_dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Buat Branch Baru", color=TEXT_MAIN,
                          weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=360,
                content=ft.Column(
                    [new_name_input, from_dd],
                    spacing=12,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Batal", on_click=_cancel,
                              style=ft.ButtonStyle(color=TEXT_MUTED)),
                ft.ElevatedButton(
                    "Buat", on_click=_do_create,
                    bgcolor=PRIMARY, color="#FFFFFF",
                ),
            ],
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(create_dialog)
        create_dialog.open = True
        page.update()

    def do_logout():
        from core.auth import delete_token
        from config import PAGE_LOGIN
        delete_token()
        state.token = ""
        state.username = ""
        navigate(PAGE_LOGIN)

    sidebar = Sidebar(
        username=state.username,
        current_page="",
        on_navigate=navigate,
        on_logout=do_logout,
        avatar_url=state.avatar_url,
    )

    content = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        content=ft.Column(
            [
                ft.Container(
                    bgcolor=BG_SURFACE,
                    border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
                    padding=ft.padding.symmetric(horizontal=20, vertical=14),
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                icon_color=TEXT_MUTED,
                                on_click=lambda _: navigate(PAGE_DASHBOARD),
                            ),
                            ft.Text(f"Branches: {repo['name']}",
                                    size=18, color=TEXT_MAIN,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True),
                            ft.ElevatedButton(
                                "Buat Branch Baru",
                                icon=ft.icons.ADD,
                                bgcolor=PRIMARY,
                                color="#FFFFFF",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=_open_create_dialog,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),

                ft.Container(
                    expand=True,
                    padding=ft.padding.all(24),
                    content=ft.Column(
                        [
                            ft.Container(
                                alignment=ft.alignment.center,
                                content=loading_ring,
                                visible=True,
                            ),
                            ft.Container(
                                expand=True,
                                content=branch_col,
                            ),
                        ],
                        expand=True,
                    ),
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )

    return ft.Row([sidebar, content], spacing=0, expand=True)
