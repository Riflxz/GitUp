# pages/clone_page.py

import asyncio
import flet as ft
from pathlib import Path
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, DANGER, ACCENT,
    PAGE_DASHBOARD
)
from core import github_api, git_ops
from core.state import AppState
from components.sidebar import Sidebar
from components import dialogs


def clone_page(page: ft.Page, state: AppState,
               navigate: callable) -> ft.Row:

    repo = state.selected_repo
    if not repo:
        navigate(PAGE_DASHBOARD)
        return ft.Row()

    default_dest = str(Path.home() / repo["name"])

    branch_dd = ft.Dropdown(
        value="",
        width=200,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        options=[],
    )

    dest_input = ft.TextField(
        value=default_dest,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        cursor_color=TEXT_MAIN,
        border_radius=8,
        expand=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
        on_change=lambda e: _check_dest(e.control.value),
    )

    dest_warning = ft.Row(
        [
            ft.Icon(ft.icons.WARNING_AMBER_OUTLINED,
                    size=15, color="#D29922"),
            ft.Text("Folder ini sudah ada isinya. "
                    "File lama mungkin tertimpa.",
                    color="#D29922", size=12),
        ],
        spacing=6,
        visible=False,
    )

    clone_btn = ft.ElevatedButton(
        "Clone Repository",
        icon=ft.icons.DOWNLOAD,
        bgcolor=PRIMARY,
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )

    def on_dir_picked(e: ft.FilePickerResultEvent):
        if e.path:
            dest_input.value = e.path
            _check_dest(e.path)
            page.update()

    dir_picker = ft.FilePicker(on_result=on_dir_picked)
    page.overlay.append(dir_picker)

    def _check_dest(path: str):
        try:
            p = Path(path)
            not_empty = p.exists() and any(p.iterdir())
            dest_warning.visible = not_empty
            page.update()
        except Exception:
            dest_warning.visible = False
            page.update()

    _check_dest(default_dest)

    async def _load_branches():
        try:
            branches = await asyncio.to_thread(
                github_api.get_branches, state.token, repo["full_name"])
            branch_dd.options = [ft.dropdown.Option(b, b) for b in branches]
            branch_dd.value   = repo.get("default_branch", "main")
            page.update()
        except Exception as e:
            dialogs.show_error(page, "Gagal Memuat Branch", str(e))

    page.run_task(_load_branches)

    async def do_clone(_):
        dest   = dest_input.value.strip()
        branch = branch_dd.value

        if not dest:
            dialogs.show_error(page, "Folder Tujuan Kosong",
                               "Tentukan folder tujuan clone.")
            return
        if not branch:
            dialogs.show_error(page, "Branch Belum Dipilih",
                               "Pilih branch yang akan di-clone.")
            return

        p = Path(dest)
        if p.exists() and any(p.iterdir()):
            dialogs.show_confirm(
                page,
                "Folder Sudah Ada Isinya",
                f"'{dest}' sudah berisi file.\nLanjutkan clone ke sini?",
                on_confirm=lambda: page.run_task(_start_clone, dest, branch),
            )
        else:
            await _start_clone(dest, branch)

    async def _start_clone(dest: str, branch: str):
        pd = dialogs.ProgressDialog(page, "Clone Repository")
        pd.show()
        clone_btn.disabled = True
        page.update()

        try:
            repo_url = repo["html_url"]
            await asyncio.to_thread(
                git_ops.clone_repo,
                repo_url=repo_url,
                dest_path=dest,
                token=state.token,
                branch=branch,
                on_progress=pd.log,
            )
            pd.close()
            clone_btn.disabled = False
            page.update()
            dialogs.show_success(
                page,
                "Clone Berhasil!",
                f"Repository berhasil di-clone ke:\n{dest}",
            )
        except Exception as e:
            pd.close()
            clone_btn.disabled = False
            page.update()
            dialogs.show_error(page, "Clone Gagal", str(e))

    clone_btn.on_click = do_clone

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
                            ft.Text(f"Clone: {repo['name']}",
                                    size=18, color=TEXT_MAIN,
                                    weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                ),

                ft.Container(
                    expand=True,
                    padding=ft.padding.all(24),
                    content=ft.Column(
                        [
                            ft.Container(
                                bgcolor=BG_SURFACE,
                                border=ft.border.all(1, BORDER),
                                border_radius=10,
                                padding=ft.padding.all(24),
                                content=ft.Column(
                                    [
                                        ft.Text("Branch", color=TEXT_MUTED,
                                                size=13,
                                                weight=ft.FontWeight.BOLD),
                                        branch_dd,
                                        ft.Container(height=16),

                                        ft.Text("Folder Tujuan",
                                                color=TEXT_MUTED, size=13,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Row(
                                            [
                                                dest_input,
                                                ft.ElevatedButton(
                                                    "Browse",
                                                    bgcolor=BG_INPUT,
                                                    color=TEXT_MAIN,
                                                    style=ft.ButtonStyle(
                                                        side=ft.BorderSide(1, BORDER),
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                    ),
                                                    on_click=lambda _:
                                                        dir_picker.get_directory_path(),
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                        dest_warning,
                                        ft.Container(height=24),

                                        ft.Row(
                                            [clone_btn],
                                            alignment=ft.MainAxisAlignment.END,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ),
                        ],
                    ),
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )

    return ft.Row([sidebar, content], spacing=0, expand=True)
