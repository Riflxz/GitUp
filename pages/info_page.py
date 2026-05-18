# pages/info_page.py

import asyncio
import flet as ft
from config import (
    BG_MAIN, BG_SURFACE, BG_INPUT, BORDER, PRIMARY,
    TEXT_MAIN, TEXT_MUTED, ACCENT, DANGER, APP_VERSION,
    PAGE_DASHBOARD
)
from core import github_api
from core.state import AppState
from components.sidebar import Sidebar
from components import dialogs


def info_page(page: ft.Page, state: AppState,
              navigate: callable) -> ft.Row:

    repo = state.selected_repo
    if not repo:
        navigate(PAGE_DASHBOARD)
        return ft.Row()

    loading      = ft.ProgressRing(color=PRIMARY, visible=True)
    tags_section = ft.Container(visible=False)
    releases_section = ft.Container(visible=False)

    info_text     = ft.Column(spacing=6, tight=True, scroll=ft.ScrollMode.AUTO)
    info_card = ft.Container(
        visible=False,
        bgcolor=BG_SURFACE,
        border=ft.border.all(1, BORDER),
        border_radius=10,
        padding=ft.padding.all(20),
        content=ft.Column([info_text], spacing=4),
    )
    tags_list     = ft.Column(spacing=4)
    releases_list = ft.Column(spacing=4)

    current_topics: list[str] = []

    def _build_url_row(label: str, url: str):
        return ft.Row(
            [
                ft.Text(label, color=TEXT_MUTED, size=12, width=120),
                ft.TextButton(
                    content=ft.Text(url, color=ACCENT, size=12, selectable=True),
                    on_click=lambda _, u=url: page.launch_url(u),
                    style=ft.ButtonStyle(padding=ft.padding.all(0)),
                ),
                ft.IconButton(
                    icon=ft.icons.CONTENT_COPY,
                    icon_size=14,
                    icon_color=TEXT_MUTED,
                    tooltip="Salin URL",
                    on_click=lambda _, u=url: _copy_url(u),
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _copy_url(url: str):
        page.set_clipboard(url)
        page.snack_bar = ft.SnackBar(
            content=ft.Row(
                [ft.Icon(ft.icons.CHECK, color="#FFFFFF", size=16),
                 ft.Text("URL disalin!", color="#FFFFFF", size=13)],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#238636",
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=8),
            duration=2000,
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        page.snack_bar.open = True
        page.update()

    def _build_topics_row(topics: list[str]):
        children = []
        if topics:
            for t in topics:
                children.append(
                    ft.Container(
                        content=ft.Text(f"#{t}", size=11, color=ACCENT, weight=ft.FontWeight.BOLD),
                        bgcolor=ACCENT + "20",
                        border=ft.border.all(1, ACCENT + "40"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    )
                )
        else:
            children.append(ft.Text("Tidak ada topics", size=11, color=TEXT_MUTED, italic=True))
        children.append(
            ft.Container(
                content=ft.IconButton(
                    icon=ft.icons.EDIT,
                    icon_size=14,
                    icon_color=TEXT_MUTED,
                    tooltip="Atur topics",
                    on_click=lambda _: _open_topics_dialog(),
                ),
                padding=ft.padding.only(left=4),
            )
        )
        container = ft.Container(
            content=ft.Row(children, spacing=6, wrap=True),
            padding=ft.padding.only(left=128),
        )
        container.is_topics_row = True
        return container

    async def _load_data():
        try:
            detail = await asyncio.to_thread(
                github_api.get_full_repo_info, state.token, repo["full_name"])

            info_text.controls.clear()
            info_text.controls.append(_info_row("Nama", detail["name"]))
            info_text.controls.append(_info_row("Deskripsi", detail["description"] or "-"))
            info_text.controls.append(_build_url_row("URL", detail["html_url"]))
            info_text.controls.append(_build_url_row("HTTPS", detail["clone_url"]))
            info_text.controls.append(_info_row("SSH", detail["ssh_url"]))
            info_text.controls.append(_info_row("Visibilitas", "Privat" if detail["private"] else "Publik"))
            info_text.controls.append(_info_row("Branch Default", detail["default_branch"]))
            info_text.controls.append(_info_row("Bahasa", detail["language"] or "-"))
            info_text.controls.append(_info_row("Stars", str(detail["stars"])))
            info_text.controls.append(_info_row("Forks", str(detail["forks"])))
            info_text.controls.append(_info_row("Issues", str(detail["open_issues"])))
            info_text.controls.append(_info_row("Dibuat", detail["created_at"]))
            info_text.controls.append(_info_row("Diupdate", detail["updated_at"]))

            nonlocal current_topics
            current_topics = detail.get("topics", [])
            info_text.controls.append(_build_topics_row(current_topics))

            loading.visible   = False
            info_card.visible = True
            page.update()

            page.run_task(_load_tags)
            page.run_task(_load_releases)

        except Exception as e:
            loading.visible = False
            page.update()
            dialogs.show_error(page, "Gagal Memuat Info", str(e))

    def _refresh_topics_display():
        nonlocal current_topics
        idx = None
        for i, c in enumerate(info_text.controls):
            if isinstance(c, ft.Container) and getattr(c, 'is_topics_row', False):
                idx = i
                break
        if idx is not None:
            row = _build_topics_row(current_topics)
            row.is_topics_row = True
            info_text.controls[idx] = row
        page.update()

    def _open_topics_dialog():
        topic_input = ft.TextField(
            label="Nama topic",
            hint_text="contoh: python, tools, github",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )

        topic_chips = ft.Row(spacing=6, wrap=True)

        def _rebuild_chips():
            topic_chips.controls.clear()
            for t in current_topics:
                topic_chips.controls.append(
                    ft.Chip(
                        label=ft.Text(f"#{t}", color=TEXT_MAIN, size=12),
                        bgcolor=BG_SURFACE,
                        delete_icon=ft.Icon(ft.icons.CLOSE, size=14, color=DANGER),
                        on_delete=lambda _, rm=t: _remove_topic(rm),
                    )
                )
            page.update()

        def _add_topic(_):
            t = topic_input.value.strip().lower().replace(" ", "-").replace("#", "")
            if t and t not in current_topics:
                current_topics.append(t)
                topic_input.value = ""
                _rebuild_chips()
                page.update()

        def _remove_topic(t: str):
            if t in current_topics:
                current_topics.remove(t)
                _rebuild_chips()

        def _save(_):
            dialog.open = False
            page.update()
            page.run_task(_do_save_topics)

        def _cancel(_):
            dialog.open = False
            page.update()

        _rebuild_chips()

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Atur Topics", color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    [
                        ft.Text("Topics membantu orang menemukan repository Anda.",
                                color=TEXT_MUTED, size=12),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                topic_input,
                                ft.ElevatedButton("Tambah", on_click=_add_topic,
                                                  bgcolor=BG_INPUT, color=TEXT_MAIN,
                                                  style=ft.ButtonStyle(
                                                      shape=ft.RoundedRectangleBorder(radius=8),
                                                      side=ft.BorderSide(1, BORDER),
                                                  )),
                            ],
                            spacing=6,
                        ),
                        topic_chips,
                    ],
                    spacing=10,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Batal", on_click=_cancel,
                              style=ft.ButtonStyle(color=TEXT_MUTED)),
                ft.ElevatedButton("Simpan Topics", on_click=_save,
                                  bgcolor=PRIMARY, color="#FFFFFF"),
            ],
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def _do_save_topics():
        try:
            await asyncio.to_thread(
                github_api.set_topics, state.token, repo["full_name"], current_topics)
            dialogs.show_success(page, "Topics Disimpan!", "Topics berhasil diperbarui.")
            _refresh_topics_display()
        except Exception as e:
            dialogs.show_error(page, "Gagal Simpan Topics", str(e))

    async def _load_tags():
        try:
            tags = await asyncio.to_thread(
                github_api.get_tags, state.token, repo["full_name"])
            tags_list.controls.clear()
            if not tags:
                tags_list.controls.append(
                    ft.Text("Belum ada tag", color=TEXT_MUTED, size=12, italic=True))
            else:
                for t in tags:
                    tags_list.controls.append(
                        ft.Container(
                            bgcolor=BG_SURFACE,
                            border=ft.border.all(1, BORDER),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.LABEL_OUTLINE, size=14, color=ACCENT),
                                    ft.Text(t["name"], size=13, color=TEXT_MAIN, expand=True),
                                    ft.Text(t["sha"][:7], size=11, color=TEXT_MUTED),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE,
                                        icon_size=16,
                                        icon_color=DANGER,
                                        tooltip="Hapus tag",
                                        on_click=lambda _, tag=t["name"]:
                                            page.run_task(_delete_tag, tag),
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        )
                    )
            tags_section.visible = True
            page.update()
        except Exception as e:
            dialogs.show_error(page, "Gagal Memuat Tags", str(e))

    async def _delete_tag(tag_name: str):
        try:
            await asyncio.to_thread(
                github_api.delete_tag, state.token, repo["full_name"], tag_name)
            dialogs.show_success(page, "Tag Dihapus!", f"Tag '{tag_name}' berhasil dihapus.")
            page.run_task(_load_tags)
        except Exception as e:
            dialogs.show_error(page, "Gagal Hapus Tag", str(e))

    async def _load_releases():
        try:
            releases = await asyncio.to_thread(
                github_api.get_releases, state.token, repo["full_name"])
            releases_list.controls.clear()
            if not releases:
                releases_list.controls.append(
                    ft.Text("Belum ada release", color=TEXT_MUTED, size=12, italic=True))
            else:
                for rl in releases:
                    releases_list.controls.append(
                        ft.Container(
                            bgcolor=BG_SURFACE,
                            border=ft.border.all(1, BORDER),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=12, vertical=10),
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.ROCKET_LAUNCH_OUTLINED, size=14, color=PRIMARY),
                                            ft.Text(rl["tag_name"], size=13, color=TEXT_MAIN,
                                                    weight=ft.FontWeight.BOLD, expand=True),
                                            ft.Text(rl["published_at"], size=11, color=TEXT_MUTED),
                                            ft.IconButton(
                                                icon=ft.icons.EDIT,
                                                icon_size=16,
                                                icon_color=ACCENT,
                                                tooltip="Edit release",
                                                on_click=lambda _, tag=rl["tag_name"], t=rl["title"], b=rl["body"], d=rl["draft"], p=rl["prerelease"]:
                                                    _open_edit_release_dialog(tag, t, b, d, p),
                                            ),
                                            ft.IconButton(
                                                icon=ft.icons.DELETE_OUTLINE,
                                                icon_size=16,
                                                icon_color=DANGER,
                                                tooltip="Hapus release",
                                                on_click=lambda _, tag=rl["tag_name"]:
                                                    _confirm_delete_release(tag),
                                            ),
                                        ],
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(rl["title"], size=12, color=TEXT_MUTED,
                                            visible=bool(rl["title"])),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                            ink=True,
                            on_click=lambda _, url=rl["html_url"]: page.launch_url(url),
                        )
                    )
            releases_section.visible = True
            page.update()
        except Exception as e:
            dialogs.show_error(page, "Gagal Memuat Releases", str(e))

    def _confirm_delete_release(tag_name: str):
        dialogs.show_confirm(
            page,
            f"Hapus Release '{tag_name}'?",
            "Release ini akan dihapus permanen dari GitHub.",
            on_confirm=lambda: page.run_task(_delete_release, tag_name),
        )

    async def _delete_release(tag_name: str):
        try:
            await asyncio.to_thread(
                github_api.delete_release, state.token, repo["full_name"], tag_name)
            dialogs.show_success(page, "Release Dihapus!",
                                 f"Release '{tag_name}' berhasil dihapus.")
            page.run_task(_load_releases)
        except Exception as e:
            dialogs.show_error(page, "Gagal Hapus Release", str(e))

    def _info_row(label: str, value: str):
        return ft.Row(
            [
                ft.Text(label, color=TEXT_MUTED, size=12, width=120),
                ft.Text(value, color=TEXT_MAIN, size=13, selectable=True, expand=True),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    page.run_task(_load_data)

    def _open_create_tag_dialog(_):
        sha_input = ft.TextField(
            label="SHA Commit (biarkan kosong untuk branch default)",
            hint_text="7 karakter atau lebih",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        name_input = ft.TextField(
            label="Nama Tag",
            hint_text="contoh: v1.0.0",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )

        async def _do_create():
            tag_name = name_input.value.strip()
            sha      = sha_input.value.strip()

            if not tag_name:
                return

            dialog.open = False
            page.update()

            try:
                if not sha:
                    sha = await asyncio.to_thread(
                        github_api.get_default_branch_sha, state.token, repo["full_name"])
                await asyncio.to_thread(
                    github_api.create_tag, state.token, repo["full_name"], tag_name, sha)
                dialogs.show_success(page, "Tag Dibuat!", f"Tag '{tag_name}' berhasil dibuat.")
                page.run_task(_load_tags)
            except Exception as e:
                dialogs.show_error(page, "Gagal Membuat Tag", str(e))

        def _cancel(_):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Buat Tag Baru", color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=360,
                content=ft.Column([name_input, sha_input], spacing=12, tight=True),
            ),
            actions=[
                ft.TextButton("Batal", on_click=_cancel,
                              style=ft.ButtonStyle(color=TEXT_MUTED)),
                ft.ElevatedButton("Buat", on_click=lambda _: page.run_task(_do_create),
                                  bgcolor=PRIMARY, color="#FFFFFF"),
            ],
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def _open_create_release_dialog(_):
        tag_input = ft.TextField(
            label="Nama Tag (contoh: v1.0.0)",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        title_input = ft.TextField(
            label="Judul Release",
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        body_input = ft.TextField(
            label="Deskripsi (opsional)",
            multiline=True,
            min_lines=3,
            max_lines=6,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )

        async def _do_create():
            tag   = tag_input.value.strip()
            title = title_input.value.strip()
            body  = body_input.value.strip()

            if not tag or not title:
                return

            dialog.open = False
            page.update()

            try:
                await asyncio.to_thread(
                    github_api.create_release,
                    state.token, repo["full_name"], tag, title, body)
                dialogs.show_success(page, "Release Dibuat!",
                                     f"Release '{tag}' berhasil dibuat.")
                page.run_task(_load_releases)
            except Exception as e:
                dialogs.show_error(page, "Gagal Membuat Release", str(e))

        def _cancel(_):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Buat Release Baru", color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                content=ft.Column([tag_input, title_input, body_input], spacing=12, tight=True),
            ),
            actions=[
                ft.TextButton("Batal", on_click=_cancel,
                              style=ft.ButtonStyle(color=TEXT_MUTED)),
                ft.ElevatedButton("Buat Release", on_click=lambda _: page.run_task(_do_create),
                                  bgcolor=PRIMARY, color="#FFFFFF"),
            ],
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def _open_edit_release_dialog(tag_name: str, cur_title: str, cur_body: str, cur_draft: bool, cur_prerelease: bool):
        title_input = ft.TextField(
            label="Judul Release",
            value=cur_title,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        body_input = ft.TextField(
            label="Deskripsi",
            value=cur_body,
            multiline=True,
            min_lines=3,
            max_lines=8,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_MAIN,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            cursor_color=TEXT_MAIN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        )
        draft_check = ft.Checkbox(
            label="Draft (tidak dipublikasikan)",
            value=cur_draft,
            label_style=ft.TextStyle(color=TEXT_MAIN),
            check_color=PRIMARY, active_color=PRIMARY,
        )
        prerelease_check = ft.Checkbox(
            label="Prerelease",
            value=cur_prerelease,
            label_style=ft.TextStyle(color=TEXT_MAIN),
            check_color=PRIMARY, active_color=PRIMARY,
        )

        async def _do_save():
            title = title_input.value.strip()
            body  = body_input.value.strip()
            draft = draft_check.value
            pre   = prerelease_check.value

            if not title:
                return

            dialog.open = False
            page.update()

            try:
                await asyncio.to_thread(
                    github_api.update_release,
                    state.token, repo["full_name"], tag_name, title, body, draft, pre)
                dialogs.show_success(page, "Release Diperbarui!",
                                     f"Release '{tag_name}' berhasil diperbarui.")
                page.run_task(_load_releases)
            except Exception as e:
                dialogs.show_error(page, "Gagal Memperbarui Release", str(e))

        def _cancel(_):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text(f"Edit Release: {tag_name}", color=TEXT_MAIN,
                          weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    [
                        ft.Text("Perbarui detail release di bawah.",
                                color=TEXT_MUTED, size=12),
                        ft.Container(height=4),
                        title_input,
                        body_input,
                        draft_check,
                        prerelease_check,
                    ],
                    spacing=10,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Batal", on_click=_cancel,
                              style=ft.ButtonStyle(color=TEXT_MUTED)),
                ft.ElevatedButton("Simpan Perubahan",
                                  on_click=lambda _: page.run_task(_do_save),
                                  bgcolor=PRIMARY, color="#FFFFFF"),
            ],
            bgcolor=BG_SURFACE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        page.overlay.append(dialog)
        dialog.open = True
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
                            ft.Text(f"Info: {repo['name']}",
                                    size=18, color=TEXT_MAIN,
                                    weight=ft.FontWeight.BOLD, expand=True),
                        ],
                        spacing=8,
                    ),
                ),

                ft.Container(
                    expand=True,
                    padding=ft.padding.all(24),
                    content=ft.Column(
                        [
                            loading,
                            info_card,
                            ft.Container(height=16),

                            tags_section,
                            ft.Container(
                                bgcolor=BG_SURFACE,
                                border=ft.border.all(1, BORDER),
                                border_radius=10,
                                padding=ft.padding.all(20),
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text("Tags", size=16, color=TEXT_MAIN,
                                                        weight=ft.FontWeight.BOLD, expand=True),
                                                ft.ElevatedButton(
                                                    "Buat Tag",
                                                    icon=ft.icons.ADD,
                                                    bgcolor=BG_INPUT,
                                                    color=TEXT_MAIN,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        side=ft.BorderSide(1, BORDER),
                                                        padding=ft.padding.symmetric(
                                                            horizontal=12, vertical=6),
                                                    ),
                                                    on_click=_open_create_tag_dialog,
                                                ),
                                            ],
                                            spacing=8,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        ft.Container(height=8),
                                        tags_list,
                                    ],
                                    spacing=4,
                                ),
                            ),

                            ft.Container(height=16),

                            releases_section,
                            ft.Container(
                                bgcolor=BG_SURFACE,
                                border=ft.border.all(1, BORDER),
                                border_radius=10,
                                padding=ft.padding.all(20),
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text("Releases", size=16, color=TEXT_MAIN,
                                                        weight=ft.FontWeight.BOLD, expand=True),
                                                ft.ElevatedButton(
                                                    "Buat Release",
                                                    icon=ft.icons.ADD,
                                                    bgcolor=BG_INPUT,
                                                    color=TEXT_MAIN,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        side=ft.BorderSide(1, BORDER),
                                                        padding=ft.padding.symmetric(
                                                            horizontal=12, vertical=6),
                                                    ),
                                                    on_click=_open_create_release_dialog,
                                                ),
                                            ],
                                            spacing=8,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        ft.Container(height=8),
                                        releases_list,
                                    ],
                                    spacing=4,
                                ),
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
