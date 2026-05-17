# pages/upload_page.py

import asyncio
import os
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, DANGER, ACCENT,
    PAGE_DASHBOARD
)
from core import github_api, git_ops
from core.state import AppState
from core.file_dialog import pick_folder_async, pick_files_async, paste_file_paths
from components.sidebar import Sidebar
from components.file_item import FileItem
from components import dialogs


def upload_page(page: ft.Page, state: AppState,
                navigate: callable) -> ft.Row:

    repo = state.selected_repo
    if not repo:
        navigate(PAGE_DASHBOARD)
        return ft.Row()

    mode           = "folder"
    selected_folder = ""
    selected_files  = []

    branch_dd = ft.Dropdown(
        value="",
        width=180,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        options=[],
    )

    folder_path_text = ft.Text("Belum ada folder dipilih",
                               color=TEXT_MUTED, size=13)

    folder_path_input = ft.TextField(
        hint_text="Ketik atau paste path folder...",
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        cursor_color=TEXT_MAIN,
        border_radius=8,
        expand=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        on_change=lambda e: _set_folder_path(e.control.value),
    )

    files_list_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)

    file_path_input = ft.TextField(
        hint_text="Ketik path file lalu tekan Enter...",
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        cursor_color=TEXT_MAIN,
        border_radius=8,
        expand=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        on_submit=lambda e: _add_manual_file(e.control.value),
    )

    commit_input = ft.TextField(
        label="Pesan commit",
        hint_text="contoh: Tambah fitur login",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    push_btn = ft.ElevatedButton(
        "Push ke GitHub",
        icon=ft.icons.UPLOAD,
        bgcolor=PRIMARY,
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )

    def _set_folder_path(path: str):
        nonlocal selected_folder
        path = path.strip()
        if path and os.path.isdir(path):
            selected_folder = path
            folder_path_text.value = path
            folder_path_text.color = TEXT_MAIN
        else:
            selected_folder = ""
            folder_path_text.value = path or "Belum ada folder dipilih"
            folder_path_text.color = TEXT_MUTED if not path else DANGER
        page.update()

    def _add_manual_file(path: str):
        path = path.strip().strip('"').strip("'")
        if not path:
            return
        if os.path.isfile(path):
            if path not in selected_files:
                selected_files.append(path)
            file_path_input.value = ""
            _render_file_list()
        else:
            dialogs.show_error(page, "File Tidak Ditemukan",
                               f"'{path}' bukan file yang valid.")
        page.update()

    def _render_file_list():
        files_list_col.controls.clear()
        for fp in selected_files:
            files_list_col.controls.append(
                FileItem(path=fp, on_remove=_remove_file)
            )
        page.update()

    def _remove_file(fp: str):
        if fp in selected_files:
            selected_files.remove(fp)
        _render_file_list()

    def _paste_folder_path():
        paths = paste_file_paths()
        if paths and os.path.isdir(paths[0]):
            folder_path_input.value = paths[0]
            _set_folder_path(paths[0])
            page.update()
        else:
            dialogs.show_error(page, "Gagal Paste", "Clipboard tidak berisi folder yang valid.")

    def _paste_file_paths_action():
        paths = paste_file_paths()
        if not paths:
            dialogs.show_error(page, "Gagal Paste", "Clipboard tidak berisi file yang valid.")
            return
        
        for p in paths:
            if os.path.isfile(p) and p not in selected_files:
                selected_files.append(p)
        _render_file_list()
        page.update()

    def _browse_folder():
        def _on_result(path: str):
            if path:
                folder_path_input.value = path
                _set_folder_path(path)
                page.update()
        pick_folder_async(_on_result)

    def _browse_files():
        def _on_result(files: list):
            for f in files:
                if f not in selected_files:
                    selected_files.append(f)
            _render_file_list()
        pick_files_async(_on_result)

    mode_tabs = ft.Tabs(
        selected_index=0,
        indicator_color=PRIMARY,
        label_color=TEXT_MAIN,
        unselected_label_color=TEXT_MUTED,
        tabs=[
            ft.Tab(text="Upload Folder"),
            ft.Tab(text="Upload File"),
        ],
        on_change=lambda e: _set_mode(e.control.selected_index),
    )

    folder_panel = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    height=100,
                    bgcolor=BG_INPUT,
                    border=ft.border.all(1, ACCENT),
                    border_radius=12,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.FOLDER_OPEN,
                                    size=30, color=ACCENT),
                            ft.Text("Klik Browse atau ketik path manual",
                                    color=TEXT_MUTED, size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        tight=True,
                    ),
                    on_click=lambda _: _browse_folder(),
                    ink=True,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.icons.FOLDER_OPEN,
                            bgcolor=BG_INPUT,
                            color=TEXT_MAIN,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER),
                            ),
                            on_click=lambda _: _browse_folder(),
                        ),
                        ft.ElevatedButton(
                            "Paste",
                            icon=ft.icons.CONTENT_PASTE,
                            bgcolor=BG_INPUT,
                            color=TEXT_MAIN,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER),
                            ),
                            on_click=lambda _: _paste_folder_path(),
                        ),
                        folder_path_input,
                    ],
                    spacing=8,
                ),
                folder_path_text,
            ],
            spacing=6,
        ),
        padding=ft.padding.all(16),
        visible=True,
    )

    files_panel = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    height=100,
                    bgcolor=BG_INPUT,
                    border=ft.border.all(1, ACCENT),
                    border_radius=12,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.ATTACH_FILE,
                                    size=30, color=ACCENT),
                            ft.Text("Klik Browse atau ketik path manual",
                                    color=TEXT_MUTED, size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        tight=True,
                    ),
                    on_click=lambda _: _browse_files(),
                    ink=True,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.icons.ATTACH_FILE,
                            bgcolor=BG_INPUT,
                            color=TEXT_MAIN,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER),
                            ),
                            on_click=lambda _: _browse_files(),
                        ),
                        ft.ElevatedButton(
                            "Paste",
                            icon=ft.icons.CONTENT_PASTE,
                            bgcolor=BG_INPUT,
                            color=TEXT_MAIN,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER),
                            ),
                            on_click=lambda _: _paste_file_paths_action(),
                        ),
                        file_path_input,
                        ft.ElevatedButton(
                            "+",
                            bgcolor=PRIMARY,
                            color="#FFFFFF",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(
                                    horizontal=14, vertical=14),
                            ),
                            on_click=lambda _: _add_manual_file(
                                file_path_input.value or ""),
                        ),
                    ],
                    spacing=8,
                ),
                files_list_col,
            ],
            spacing=6,
        ),
        padding=ft.padding.all(16),
        visible=False,
    )

    def _set_mode(idx: int):
        nonlocal mode
        mode              = "folder" if idx == 0 else "files"
        folder_panel.visible = (mode == "folder")
        files_panel.visible  = (mode == "files")
        page.update()

    async def _load_branches():
        try:
            branches = await asyncio.to_thread(
                github_api.get_branches, state.token, repo["full_name"])
            branch_dd.options = [
                ft.dropdown.Option(b, b) for b in branches]
            branch_dd.value = repo.get("default_branch", "main")
            page.update()
        except Exception:
            branch_dd.options = [
                ft.dropdown.Option("main", "main")]
            branch_dd.value = "main"
            page.update()

    page.run_task(_load_branches)

    async def do_push(_):
        commit_msg = commit_input.value.strip()
        branch     = branch_dd.value

        if not commit_msg:
            dialogs.show_error(page, "Pesan Commit Kosong",
                               "Isi pesan commit sebelum push.")
            return

        if not branch:
            dialogs.show_error(page, "Branch Belum Dipilih",
                               "Pilih branch tujuan terlebih dahulu.")
            return

        if mode == "folder":
            if not selected_folder or not os.path.isdir(selected_folder):
                dialogs.show_error(
                    page, "Folder Tidak Valid",
                    "Pilih folder yang valid terlebih dahulu.")
                return
        elif mode == "files" and not selected_files:
            dialogs.show_error(page, "File Belum Dipilih",
                               "Pilih setidaknya satu file.")
            return

        pd = dialogs.ProgressDialog(page, "Push ke GitHub")
        pd.show()
        push_btn.disabled = True
        page.update()

        try:
            repo_url = repo["html_url"]
            if mode == "folder":
                await asyncio.to_thread(
                    git_ops.push_folder,
                    folder_path=selected_folder,
                    repo_url=repo_url,
                    token=state.token,
                    branch=branch,
                    commit_message=commit_msg,
                    on_progress=pd.log,
                )
            else:
                await asyncio.to_thread(
                    git_ops.push_files,
                    file_paths=selected_files,
                    repo_url=repo_url,
                    token=state.token,
                    branch=branch,
                    commit_message=commit_msg,
                    on_progress=pd.log,
                )
            pd.close()
            push_btn.disabled = False
            page.update()
            dialogs.show_success(page, "Push Berhasil!", "Push berhasil.")
        except Exception as e:
            pd.close()
            push_btn.disabled = False
            page.update()
            dialogs.show_error(page, "Push Gagal", str(e))

    push_btn.on_click = do_push

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
                            ft.Column(
                                [
                                    ft.Text(f"Upload ke: {repo['name']}",
                                            size=18, color=TEXT_MAIN,
                                            weight=ft.FontWeight.BOLD),
                                    ft.Text("Branch tujuan:",
                                            size=12, color=TEXT_MUTED),
                                ],
                                spacing=2, tight=True,
                            ),
                            branch_dd,
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
                                content=ft.Column(
                                    [mode_tabs, folder_panel, files_panel],
                                    spacing=0,
                                ),
                            ),
                            ft.Container(height=16),
                            ft.Container(
                                bgcolor=BG_SURFACE,
                                border=ft.border.all(1, BORDER),
                                border_radius=10,
                                padding=ft.padding.all(16),
                                content=ft.Column(
                                    [
                                        ft.Text("Pesan Commit",
                                                color=TEXT_MUTED, size=13,
                                                weight=ft.FontWeight.BOLD),
                                        commit_input,
                                    ],
                                    spacing=8,
                                ),
                            ),
                            ft.Container(height=16),
                            ft.Row(
                                [push_btn],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )

    return ft.Row([sidebar, content], spacing=0, expand=True)
