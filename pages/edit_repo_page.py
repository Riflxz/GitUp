# pages/edit_repo_page.py

import asyncio
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY, PRIMARY_H,
    TEXT_MAIN, TEXT_MUTED, DANGER, ACCENT,
    PAGE_DASHBOARD
)
from core import github_api
from core.state import AppState
from components.sidebar import Sidebar
from components import dialogs


def edit_repo_page(page: ft.Page, state: AppState,
                   navigate: callable) -> ft.Row:

    repo = state.selected_repo
    if not repo:
        navigate(PAGE_DASHBOARD)
        return ft.Row()

    loading = ft.ProgressRing(color=PRIMARY, visible=True)
    form_container = ft.Container(visible=False)

    name_input = ft.TextField(
        label="Nama Repository",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    visibility_group = ft.RadioGroup(
        value="publik",
        content=ft.Row(
            [
                ft.Radio(value="publik", label="Publik",
                         label_style=ft.TextStyle(color=TEXT_MAIN)),
                ft.Radio(value="privat", label="Privat",
                         label_style=ft.TextStyle(color=TEXT_MAIN)),
            ],
            spacing=24,
        ),
    )

    desc_input = ft.TextField(
        label="Deskripsi",
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

    homepage_input = ft.TextField(
        label="Homepage URL (opsional)",
        hint_text="https://...",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_MAIN,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        cursor_color=TEXT_MAIN,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    default_branch_text = ft.Text("", color=TEXT_MAIN, size=13)

    has_issues_check = ft.Checkbox(
        label="Issues (pelacakan masalah)",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )
    has_projects_check = ft.Checkbox(
        label="Projects (papan proyek)",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )
    has_wiki_check = ft.Checkbox(
        label="Wiki (dokumentasi)",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )

    squash_merge_check = ft.Checkbox(
        label="Allow squash merging",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )
    merge_commit_check = ft.Checkbox(
        label="Allow merge commits",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )
    rebase_merge_check = ft.Checkbox(
        label="Allow rebase merging",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )

    delete_branch_check = ft.Checkbox(
        label="Hapus branch otomatis setelah merge",
        label_style=ft.TextStyle(color=TEXT_MAIN),
        check_color=PRIMARY, active_color=PRIMARY,
    )

    archived_check = ft.Checkbox(
        label="Arsipkan repository (read-only)",
        label_style=ft.TextStyle(color=DANGER),
        check_color=DANGER, active_color=DANGER,
    )

    save_btn = ft.ElevatedButton(
        "Simpan Pengaturan",
        bgcolor=PRIMARY,
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )

    async def _load_detail():
        nonlocal repo
        try:
            detail = await asyncio.to_thread(
                github_api.get_repo_detail, state.token, repo["full_name"])
            repo = {**repo, **detail}

            name_input.value = detail["name"]
            visibility_group.value = "privat" if detail["private"] else "publik"
            desc_input.value = detail["description"]
            homepage_input.value = detail["homepage"]
            default_branch_text.value = detail["default_branch"]
            has_issues_check.value = detail["has_issues"]
            has_projects_check.value = detail["has_projects"]
            has_wiki_check.value = detail["has_wiki"]
            squash_merge_check.value = detail["allow_squash_merge"]
            merge_commit_check.value = detail["allow_merge_commit"]
            rebase_merge_check.value = detail["allow_rebase_merge"]
            delete_branch_check.value = detail["delete_branch_on_merge"]
            archived_check.value = detail["archived"]

            loading.visible = False
            form_container.visible = True
            nonlocal default_branch
            default_branch = detail["default_branch"]
            file_manager_section.visible = True
            page.update()
            _navigate_to("")
        except Exception as e:
            loading.visible = False
            page.update()
            dialogs.show_error(page, "Gagal Memuat Detail", str(e))

    page.run_task(_load_detail)

    async def _navigate_dashboard():
        navigate(PAGE_DASHBOARD)

    async def do_save(_):
        new_name = name_input.value.strip()
        if not new_name:
            dialogs.show_error(page, "Nama Wajib Diisi",
                               "Nama repository tidak boleh kosong.")
            return

        save_btn.disabled = True
        save_btn.text = "Menyimpan..."
        page.update()

        try:
            await asyncio.to_thread(
                github_api.update_repo,
                token=state.token,
                full_name=repo["full_name"],
                name=new_name,
                private=(visibility_group.value == "privat"),
                description=desc_input.value.strip(),
                homepage=homepage_input.value.strip(),
                has_issues=has_issues_check.value,
                has_projects=has_projects_check.value,
                has_wiki=has_wiki_check.value,
                allow_squash_merge=squash_merge_check.value,
                allow_merge_commit=merge_commit_check.value,
                allow_rebase_merge=rebase_merge_check.value,
                delete_branch_on_merge=delete_branch_check.value,
                archived=archived_check.value,
            )
            save_btn.disabled = False
            save_btn.text = "Simpan Pengaturan"
            dialogs.show_success(
                page,
                "Pengaturan Disimpan!",
                "Repository berhasil diperbarui.",
                on_close=lambda: page.run_task(
                    _navigate_dashboard),
            )
        except Exception as e:
            save_btn.disabled = False
            save_btn.text = "Simpan Pengaturan"
            page.update()
            dialogs.show_error(page, "Gagal Menyimpan", str(e))

    save_btn.on_click = do_save

    # ── File Manager ───────────────────────────────────────────
    current_path = ""
    default_branch = ""
    file_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    file_manager_section = ft.Container(visible=False)

    async def _load_contents(path: str):
        try:
            items = await asyncio.to_thread(
                github_api.get_contents, state.token, repo["full_name"], path)
            file_list.controls.clear()

            if path:
                file_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [ft.Icon(ft.icons.ARROW_UPWARD, size=16, color=ACCENT),
                             ft.Text(".. (kembali)", size=13, color=ACCENT)],
                            spacing=6,
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        border_radius=6,
                        ink=True,
                        on_click=lambda _: _navigate_to(
                            "/".join(current_path.split("/")[:-1])),
                    )
                )

            for item in sorted(items, key=lambda x: (x["type"] != "dir", x["name"])):
                is_dir = item["type"] == "dir"
                file_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.icons.FOLDER if is_dir else ft.icons.DESCRIPTION,
                                    size=18,
                                    color=ACCENT if is_dir else TEXT_MUTED,
                                ),
                                ft.Text(item["name"], size=13, color=TEXT_MAIN,
                                        expand=True),
                                ft.Text(
                                    _format_size(item["size"]), size=11,
                                    color=TEXT_MUTED,
                                    visible=not is_dir,
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_size=16,
                                    icon_color=ACCENT,
                                    tooltip="Edit file",
                                    visible=not is_dir,
                                    on_click=lambda _, p=item["path"]:
                                        _open_edit_dialog(p),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=DANGER,
                                    tooltip="Hapus",
                                    on_click=lambda _, p=item["path"], d=is_dir:
                                        _confirm_delete(p, d),
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        border_radius=6,
                        ink=True,
                        on_click=lambda _, p=item["path"], d=is_dir:
                            _navigate_to(p) if d else _open_edit_dialog(p),
                    )
                )
            page.update()
        except Exception as e:
            dialogs.show_error(page, "Gagal Memuat File", str(e))

    def _navigate_to(path: str):
        nonlocal current_path
        current_path = path
        path_text.value = f"/{path}" if path else "/"
        page.run_task(_load_contents, path)

    def _format_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / 1024 ** 2:.1f} MB"

    def _open_edit_dialog(path: str):
        page.run_task(_do_open_edit, path)

    async def _do_open_edit(path: str):
        try:
            data = await asyncio.to_thread(
                github_api.get_file_content, state.token, repo["full_name"], path)
        except Exception as e:
            dialogs.show_error(page, "Gagal Membaca File", str(e))
            return

        lines = data["content"].count("\n") + 1

        editor_bg = "#1E1E1E"
        editor_fg = "#D4D4D4"
        line_bg  = "#252526"

        undo_stack = [data["content"]]
        redo_stack = []
        undo_btn = ft.IconButton(
            icon=ft.icons.UNDO, icon_size=16, icon_color="#858585",
            tooltip="Undo (Ctrl+Z)", disabled=True,
            on_click=lambda _: _undo(),
        )
        redo_btn = ft.IconButton(
            icon=ft.icons.REDO, icon_size=16, icon_color="#858585",
            tooltip="Redo (Ctrl+Shift+Z)", disabled=True,
            on_click=lambda _: _redo(),
        )

        content_input = ft.TextField(
            value=data["content"],
            multiline=True,
            min_lines=8,
            max_lines=20,
            bgcolor=editor_bg,
            border_color="#3C3C3C",
            focused_border_color=PRIMARY,
            color=editor_fg,
            cursor_color="#AEAFAD",
            border_radius=6,
            text_style=ft.TextStyle(
                font_family="Consolas, 'Courier New', monospace",
                size=13,
            ),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

        line_count_text = ft.Text(f"{lines} lines", size=11, color="#858585")
        char_count_text = ft.Text(f"{len(data['content'])} chars", size=11, color="#858585")

        _push_version = 0

        def _update_stats(e):
            current = content_input.value
            lc = current.count("\n") + 1
            line_count_text.value = f"{lc} lines"
            char_count_text.value = f"{len(current)} chars"
            nonlocal _push_version
            _push_version += 1
            page.run_task(_push_delayed, _push_version)

        async def _push_delayed(version: int):
            await asyncio.sleep(0.3)
            if version == _push_version:
                _push_undo_state()
                page.update()

        def _undo():
            if undo_stack:
                current = content_input.value
                redo_stack.append(current)
                prev = undo_stack.pop()
                content_input.value = prev
                undo_btn.disabled = len(undo_stack) <= 1
                redo_btn.disabled = False
                _update_stats(None)
                page.update()

        def _redo():
            if redo_stack:
                current = content_input.value
                undo_stack.append(current)
                nxt = redo_stack.pop()
                content_input.value = nxt
                redo_btn.disabled = not redo_stack
                undo_btn.disabled = False
                _update_stats(None)
                page.update()

        def _push_undo_state():
            current = content_input.value
            if not undo_stack or current != undo_stack[-1]:
                undo_stack.append(current)
                redo_stack.clear()
                undo_btn.disabled = False
                redo_btn.disabled = True

        content_input.on_change = _update_stats

        save_btn = ft.ElevatedButton(
            "Simpan",
            on_click=lambda _: page.run_task(_save_edit, save_btn),
            bgcolor=PRIMARY,
            color="#FFFFFF",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=20, vertical=8),
            ),
        )

        async def _save_edit(btn):
            btn.disabled = True
            btn.text = "Menyimpan..."
            page.update()
            new_content = content_input.value
            try:
                await asyncio.to_thread(
                    github_api.update_file,
                    state.token, repo["full_name"], path,
                    new_content, f"Update {path}", data["sha"],
                    default_branch,
                )
                dialog.open = False
                page.update()
                dialogs.show_success(page, "File Disimpan!",
                                     f"{path} berhasil diperbarui.")
                page.run_task(_load_contents, current_path)
            except Exception as e:
                btn.disabled = False
                btn.text = "Simpan"
                dialog.open = False
                page.update()
                dialogs.show_error(page, "Gagal Simpan File", str(e))

        def _cancel(_):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=False,
            title_padding=ft.padding.all(0),
            content_padding=ft.padding.all(0),
            actions_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            title=ft.Container(
                bgcolor="#2D2D2D",
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.CODE, size=16, color="#858585"),
                        ft.Container(width=8),
                        ft.Text(data["name"], size=13, color=editor_fg,
                                weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            bgcolor="#3C3C3C",
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            content=ft.Text(
                                _format_size(data["size"]), size=10,
                                color="#858585",
                            ),
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            content=ft.Container(
                width=720,
                bgcolor=editor_bg,
                padding=ft.padding.all(0),
                content=ft.Column(
                    [
                        ft.Container(
                            bgcolor=line_bg,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            content=ft.Row(
                                [
                                    undo_btn,
                                    redo_btn,
                                    ft.Container(
                                        width=1, height=16, bgcolor="#3C3C3C",
                                        margin=ft.margin.symmetric(horizontal=4),
                                    ),
                                    ft.Text(f"/{data['path']}", size=11,
                                            color="#858585", expand=True),
                                    ft.TextButton(
                                        content=ft.Text("Salin Konten", size=11,
                                                        color=ACCENT),
                                        style=ft.ButtonStyle(padding=ft.padding.all(0)),
                                        on_click=lambda _: (
                                            page.set_clipboard(content_input.value),
                                            page.update(),
                                        ),
                                    ),
                                ],
                                spacing=4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ),
                        ft.Divider(height=1, color="#3C3C3C"),
                        ft.Container(
                            content=content_input,
                            height=360,
                        ),
                        ft.Divider(height=1, color="#3C3C3C"),
                        ft.Container(
                            bgcolor=line_bg,
                            padding=ft.padding.symmetric(horizontal=16, vertical=5),
                            content=ft.Row(
                                [line_count_text, ft.Text("|", size=11, color="#3C3C3C"),
                                 char_count_text],
                                spacing=6,
                            ),
                        ),
                    ],
                    spacing=0,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Batal",
                    on_click=_cancel,
                    style=ft.ButtonStyle(
                        color="#858585",
                        shape=ft.RoundedRectangleBorder(radius=6),
                        side=ft.BorderSide(1, "#3C3C3C"),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    ),
                ),
                save_btn,
            ],
            bgcolor="#2D2D2D",
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def _confirm_delete(path: str, is_dir: bool):
        if is_dir:
            dialogs.show_confirm(
                page,
                f"Hapus Folder '{path}'?",
                "Folder akan dihapus beserta semua isinya. "
                "Tindakan ini tidak dapat dibatalkan.",
                on_confirm=lambda: page.run_task(_do_delete, path, is_dir),
            )
        else:
            dialogs.show_confirm(
                page,
                f"Hapus File '{path}'?",
                "File akan dihapus permanen dari repository.",
                on_confirm=lambda: page.run_task(_do_delete, path, is_dir),
            )

    async def _do_delete(path: str, is_dir: bool):
        try:
            if is_dir:
                _delete_dir(path)
            else:
                data = await asyncio.to_thread(
                    github_api.get_file_content, state.token,
                    repo["full_name"], path)
                await asyncio.to_thread(
                    github_api.delete_file,
                    state.token, repo["full_name"], path,
                    f"Hapus {path}", data["sha"], default_branch)
            dialogs.show_success(page, "Berhasil Dihapus!",
                                 f"{path} berhasil dihapus.")
            page.run_task(_load_contents, current_path)
        except Exception as e:
            dialogs.show_error(page, "Gagal Menghapus", str(e))

    async def _delete_dir(path: str):
        try:
            items = await asyncio.to_thread(
                github_api.get_contents, state.token, repo["full_name"], path)
            for item in items:
                p = item["path"]
                if item["type"] == "dir":
                    await _delete_dir(p)
                else:
                    data = await asyncio.to_thread(
                        github_api.get_file_content, state.token,
                        repo["full_name"], p)
                    await asyncio.to_thread(
                        github_api.delete_file,
                        state.token, repo["full_name"], p,
                        f"Hapus {p}", data["sha"], default_branch)
        except Exception as e:
            raise Exception(f"Gagal menghapus folder: {e}")

    path_text = ft.Text("/", size=13, color=ACCENT, weight=ft.FontWeight.BOLD)

    file_manager_section.content = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("File Manager", size=16, color=TEXT_MAIN,
                            weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        icon_size=18,
                        icon_color=TEXT_MUTED,
                        tooltip="Refresh",
                        on_click=lambda _: _navigate_to(current_path),
                    ),
                ],
                spacing=8,
            ),
            ft.Container(height=8),
            ft.Container(
                bgcolor=BG_INPUT,
                border=ft.border.all(1, BORDER),
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.FOLDER_OPEN, size=16, color=ACCENT),
                        path_text,
                    ],
                    spacing=6,
                ),
                ink=True,
                on_click=lambda _: _navigate_to(""),
            ),
            ft.Container(height=4),
            ft.Container(
                bgcolor=BG_INPUT,
                border=ft.border.all(1, BORDER),
                border_radius=8,
                padding=ft.padding.all(6),
                content=file_list,
                height=300,
                # scroll
            ),
        ],
        spacing=4,
    )

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
                        ft.Text(f"Settings: {repo.get('name', '')}",
                                size=20, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),

                ft.Container(
                    content=ft.Column(
                        [loading, form_container],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

    form_container.content = ft.Column(
        [
            ft.Container(
                bgcolor=BG_SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=10,
                padding=ft.padding.all(24),
                content=ft.Column(
                    [
                        ft.Text("Informasi Repository",
                                size=16, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=12),
                        name_input,
                        ft.Container(height=8),
                        ft.Text("Visibilitas", size=13, color=TEXT_MUTED,
                                weight=ft.FontWeight.BOLD),
                        visibility_group,
                        ft.Container(height=8),
                        desc_input,
                        ft.Container(height=8),
                        homepage_input,
                        ft.Container(height=8),
                        ft.Text("Default branch:", size=13,
                                color=TEXT_MUTED),
                        default_branch_text,
                    ],
                    spacing=4,
                ),
            ),
            ft.Container(height=16),

            ft.Container(
                bgcolor=BG_SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=10,
                padding=ft.padding.all(24),
                content=ft.Column(
                    [
                        ft.Text("Fitur Repository",
                                size=16, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        has_issues_check,
                        has_projects_check,
                        has_wiki_check,
                    ],
                    spacing=4,
                ),
            ),
            ft.Container(height=16),

            ft.Container(
                bgcolor=BG_SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=10,
                padding=ft.padding.all(24),
                content=ft.Column(
                    [
                        ft.Text("Pengaturan Merge",
                                size=16, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        squash_merge_check,
                        merge_commit_check,
                        rebase_merge_check,
                        ft.Divider(height=1, color=BORDER),
                        delete_branch_check,
                    ],
                    spacing=4,
                ),
            ),
            ft.Container(height=16),

            ft.Container(
                bgcolor=BG_SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=10,
                padding=ft.padding.all(24),
                content=ft.Column(
                    [
                        ft.Text("Status Repository",
                                size=16, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        archived_check,
                        ft.Text(
                            "Mengarsipkan repo membuatnya read-only. "
                            "Tindakan ini dapat dibatalkan.",
                            size=12, color=TEXT_MUTED,
                        ),
                    ],
                    spacing=4,
                ),
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
                    save_btn,
                ],
                spacing=12,
            ),

            file_manager_section,
        ],
        spacing=0,
    )

    return ft.Row([sidebar, form], spacing=0, expand=True)
