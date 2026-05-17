# pages/create_repo_page.py

import asyncio
import os
import re
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, DANGER, ACCENT,
    PAGE_DASHBOARD
)
from core import github_api
from core.file_dialog import pick_file
from core.state import AppState
from components.sidebar import Sidebar
from components import dialogs


_REPO_NAME_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,98}[a-zA-Z0-9]$|^[a-zA-Z0-9]$')


def create_repo_page(page: ft.Page, state: AppState,
                     navigate: callable) -> ft.Row:

    is_private  = False
    selected_gitignore = ""
    license_file_path = ""
    existing_repo_names: set[str] = set()

    name_input = ft.TextField(
        label="Nama Repository",
        hint_text="contoh: my-project",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    name_hint = ft.Text("", size=12, visible=False)

    desc_input = ft.TextField(
        label="Deskripsi (opsional)",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        max_lines=3,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    visibility_group = ft.RadioGroup(
        value="publik",
        content=ft.Row(
            [
                ft.Radio(value="publik",  label="Publik",
                         label_style=ft.TextStyle(color=TEXT_MAIN)),
                ft.Radio(value="privat", label="Privat",
                         label_style=ft.TextStyle(color=TEXT_MAIN)),
            ],
            spacing=24,
        ),
        on_change=lambda e: _set_private(e.control.value == "privat"),
    )

    gitignore_search = ft.TextField(
        label="Cari template .gitignore",
        hint_text="Ketik untuk mencari...",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        prefix_icon=ft.icons.SEARCH,
    )

    all_gitignore_templates: list[str] = []
    gitignore_list_view = ft.Column(spacing=2, tight=True, scroll=ft.ScrollMode.AUTO)
    gitignore_list_container = ft.Container(
        content=gitignore_list_view,
        height=200,
        border=ft.border.all(1, BORDER),
        border_radius=8,
        bgcolor=BG_INPUT,
        padding=ft.padding.all(4),
        visible=False,
    )

    gitignore_selected_text = ft.Text(
        "Tidak ada",
        color=TEXT_MUTED,
        size=13,
    )

    def _rebuild_gitignore_list(filter_text: str = ""):
        gitignore_list_view.controls.clear()
        filtered = [
            t for t in all_gitignore_templates
            if filter_text.lower() in t.lower()
        ] if filter_text else all_gitignore_templates

        if not filtered:
            gitignore_list_view.controls.append(
                ft.Text("Tidak ada template", color=TEXT_MUTED, size=12, italic=True)
            )
        else:
            for t in filtered:
                is_active = (t == selected_gitignore)
                gitignore_list_view.controls.append(
                    ft.Container(
                        content=ft.Text(t, color=TEXT_MAIN if is_active else TEXT_MUTED, size=13),
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        border_radius=6,
                        bgcolor=ACCENT + "20" if is_active else None,
                        on_click=lambda _, tmpl=t: _select_gitignore(tmpl),
                        ink=True,
                    )
                )
        gitignore_list_container.visible = bool(all_gitignore_templates)
        page.update()

    def _select_gitignore(template: str):
        nonlocal selected_gitignore
        selected_gitignore = template
        gitignore_selected_text.value = template
        gitignore_selected_text.color = TEXT_MAIN
        gitignore_search.value = ""
        _rebuild_gitignore_list()
        gitignore_list_container.visible = False
        page.update()

    def _on_gitignore_search(e):
        _rebuild_gitignore_list(e.control.value)

    gitignore_search.on_change = _on_gitignore_search

    def _toggle_gitignore_list(_):
        if all_gitignore_templates:
            gitignore_list_container.visible = not gitignore_list_container.visible
            if gitignore_list_container.visible:
                _rebuild_gitignore_list(gitignore_search.value)
            page.update()

    license_path_text = ft.Text(
        "Belum ada file dipilih",
        color=TEXT_MUTED,
        size=13,
        italic=True,
        expand=True,
    )

    def _pick_license_file(_):
        nonlocal license_file_path
        path = pick_file(title="Pilih File Lisensi")
        if path:
            license_file_path = path
            fname = os.path.basename(path)
            license_path_text.value = fname
            license_path_text.color = TEXT_MAIN
            license_path_text.italic = False
            page.update()

    def _clear_license(_):
        nonlocal license_file_path
        license_file_path = ""
        license_path_text.value = "Belum ada file dipilih"
        license_path_text.color = TEXT_MUTED
        license_path_text.italic = True
        page.update()

    submit_btn = ft.ElevatedButton(
        "Buat Repository",
        bgcolor=PRIMARY,
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )

    def _validate_name(e):
        val = e.control.value.strip()
        if not val:
            name_hint.value   = ""
            name_hint.visible = False
        elif not _REPO_NAME_RE.match(val):
            name_hint.value   = "\u2717 Hanya huruf, angka, - _ . (tidak boleh diawali - atau .)"
            name_hint.color   = DANGER
            name_hint.visible = True
        elif val in existing_repo_names:
            name_hint.value   = "\u2717 Nama sudah digunakan"
            name_hint.color   = DANGER
            name_hint.visible = True
        else:
            name_hint.value   = "\u2713 Nama valid"
            name_hint.color   = PRIMARY
            name_hint.visible = True
        page.update()

    name_input.on_change = _validate_name

    def _set_private(val: bool):
        nonlocal is_private
        is_private = val

    async def _load_initial_data():
        try:
            gi = await asyncio.to_thread(github_api.get_gitignore_templates, state.token)
            all_gitignore_templates.extend(gi)
            _rebuild_gitignore_list()
        except Exception:
            pass
        try:
            repos = await asyncio.to_thread(github_api.get_repos, state.token)
            existing_repo_names.update(r["name"] for r in repos)
        except Exception:
            pass
        page.update()

    page.run_task(_load_initial_data)

    async def do_create(_):
        nonlocal is_private
        name = name_input.value.strip()

        if not name:
            dialogs.show_error(page, "Nama Wajib Diisi",
                               "Nama repository tidak boleh kosong.")
            return

        if not _REPO_NAME_RE.match(name):
            dialogs.show_error(page, "Nama Tidak Valid",
                               "Gunakan huruf, angka, - _ . saja.\n"
                               "Tidak boleh diawali dengan - atau .")
            return

        if name in existing_repo_names:
            dialogs.show_error(page, "Nama Sudah Digunakan",
                               f"Repository dengan nama '{name}' sudah ada.\n"
                               "Gunakan nama yang berbeda.")
            return

        submit_btn.disabled = True
        submit_btn.text     = "Membuat..."
        page.update()

        try:
            repo_data = await asyncio.to_thread(
                github_api.create_repo,
                token=state.token,
                name=name,
                description=desc_input.value.strip(),
                private=is_private,
                gitignore_template=selected_gitignore,
                license_template="",
            )

            if license_file_path:
                try:
                    await asyncio.to_thread(
                        github_api.upload_file_to_repo,
                        token=state.token,
                        full_name=repo_data["full_name"],
                        file_path=license_file_path,
                        target_path="LICENSE",
                        branch=repo_data["default_branch"],
                        message="Add LICENSE",
                    )
                except Exception:
                    pass

            submit_btn.disabled = False
            submit_btn.text     = "Buat Repository"
            state.pending_success = f"Repository '{name}' berhasil dibuat!"
            navigate(PAGE_DASHBOARD)

        except Exception as e:
            submit_btn.disabled = False
            submit_btn.text     = "Buat Repository"
            page.update()
            dialogs.show_error(page, "Gagal Membuat Repository", str(e))

    submit_btn.on_click = do_create

    def do_logout():
        from core.auth import delete_token
        from config import PAGE_LOGIN
        delete_token()
        state.token = ""
        state.username = ""
        navigate(PAGE_LOGIN)

    sidebar = Sidebar(
        username=state.username,
        current_page="create_repo",
        on_navigate=navigate,
        on_logout=do_logout,
        avatar_url=state.avatar_url,
    )

    form = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        padding=ft.padding.all(24),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=TEXT_MUTED,
                            on_click=lambda _: navigate(PAGE_DASHBOARD),
                        ),
                        ft.Text("Buat Repository Baru", size=20,
                                color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Container(height=16),

                ft.Container(
                    bgcolor=BG_SURFACE,
                    border=ft.border.all(1, BORDER),
                    border_radius=10,
                    padding=ft.padding.all(24),
                    content=ft.Column(
                        [
                            name_input,
                            name_hint,
                            ft.Container(height=4),
                            desc_input,
                            ft.Container(height=12),

                            ft.Text("Visibilitas", size=13,
                                    color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                            visibility_group,
                            ft.Container(height=8),

                            ft.Text(".gitignore", size=13,
                                    color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                gitignore_selected_text,
                                                ft.Icon(
                                                    ft.icons.ARROW_DROP_DOWN,
                                                    color=TEXT_MUTED, size=20,
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                        padding=ft.padding.symmetric(
                                            horizontal=12, vertical=10),
                                        border=ft.border.all(1, BORDER),
                                        border_radius=8,
                                        bgcolor=BG_INPUT,
                                        expand=True,
                                        on_click=_toggle_gitignore_list,
                                        ink=True,
                                    ),
                                ],
                            ),
                            ft.Container(height=2),
                            gitignore_search,
                            ft.Container(height=2),
                            gitignore_list_container,
                            ft.Container(height=12),

                            ft.Text("Lisensi", size=13,
                                    color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Pilih File Lisensi...",
                                        icon=ft.icons.UPLOAD_FILE,
                                        bgcolor=BG_INPUT,
                                        color=TEXT_MAIN,
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            side=ft.BorderSide(1, BORDER),
                                            padding=ft.padding.symmetric(
                                                horizontal=14, vertical=10),
                                        ),
                                        on_click=_pick_license_file,
                                    ),
                                    license_path_text,
                                    ft.IconButton(
                                        icon=ft.icons.CLOSE,
                                        icon_color=TEXT_MUTED,
                                        icon_size=16,
                                        tooltip="Hapus file lisensi",
                                        on_click=_clear_license,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(height=20),

                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Batal",
                                        style=ft.ButtonStyle(
                                            color=TEXT_MUTED,
                                            side=ft.BorderSide(1, BORDER),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            padding=ft.padding.symmetric(
                                                horizontal=20, vertical=14),
                                        ),
                                        on_click=lambda _: navigate(PAGE_DASHBOARD),
                                    ),
                                    submit_btn,
                                ],
                                spacing=12,
                            ),
                        ],
                        spacing=8,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    return ft.Row([sidebar, form], spacing=0, expand=True)
