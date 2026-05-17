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
            page.update()
        except Exception as e:
            loading.visible = False
            page.update()
            dialogs.show_error(page, "Gagal Memuat Detail", str(e))

    page.run_task(_load_detail)

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
                on_close=lambda: navigate(PAGE_DASHBOARD),
            )
        except Exception as e:
            save_btn.disabled = False
            save_btn.text = "Simpan Pengaturan"
            page.update()
            dialogs.show_error(page, "Gagal Menyimpan", str(e))

    save_btn.on_click = do_save

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
        ],
        spacing=0,
    )

    return ft.Row([sidebar, form], spacing=0, expand=True)
