# components/repo_card.py

import flet as ft
from config import (
    BG_SURFACE, BG_INPUT, BORDER, PRIMARY, DANGER,
    TEXT_MAIN, TEXT_MUTED, ACCENT, BADGE_PRIV, BADGE_PUB
)


class RepoCard(ft.UserControl):
    def __init__(
        self,
        repo: dict,
        on_upload: callable,
        on_clone: callable,
        on_branches: callable,
        on_delete: callable,
        on_settings: callable = None,
        on_info: callable = None,
    ):
        super().__init__()
        self.repo       = repo
        self.on_upload   = on_upload
        self.on_clone    = on_clone
        self.on_branches = on_branches
        self.on_delete   = on_delete
        self.on_settings = on_settings
        self.on_info     = on_info

        self._border_color = BORDER

    def build(self):
        r = self.repo

        badge_color = BADGE_PRIV if r["private"] else BADGE_PUB
        badge_label = "Privat"   if r["private"] else "Publik"

        badge = ft.Container(
            content=ft.Text(badge_label, size=10, color="#FFFFFF",
                            weight=ft.FontWeight.BOLD),
            bgcolor=badge_color,
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

        def action_btn(label: str, icon, color: str, cb: callable):
            return ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=13, color=color),
                        ft.Text(label, size=12, color=color),
                    ],
                    spacing=3,
                    tight=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                on_click=lambda _, repo=self.repo: cb(repo),
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=8, vertical=6),
                    overlay_color=ft.colors.with_opacity(0.1, color),
                    shape=ft.RoundedRectangleBorder(radius=6),
                    animation_duration=150,
                ),
            )

        card_border = ft.Ref[ft.Container]()

        def on_hover(e: ft.HoverEvent):
            is_hovering = e.data == "true"
            c = card_border.current
            c.border = ft.border.all(
                1.5 if is_hovering else 1,
                ACCENT if is_hovering else BORDER,
            )
            c.shadow = (
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=14,
                    color=ft.colors.with_opacity(0.3, ACCENT),
                    offset=ft.Offset(0, 4),
                )
                if is_hovering else None
            )
            c.scale = ft.transform.Scale(1.02) if is_hovering else ft.transform.Scale(1.0)
            c.update()

        return ft.Container(
            ref=card_border,
            bgcolor=BG_SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            animate=ft.animation.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            animate_scale=ft.animation.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=on_hover,
            content=ft.Column(
                tight=True,
                spacing=6,
                controls=[
                    ft.Row(
                        [
                            ft.Icon(ft.icons.FOLDER_OUTLINED,
                                    size=15, color=ACCENT),
                            ft.Text(
                                r["name"],
                                color=ACCENT,
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            ),
                            badge,
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        r.get("description") or "Tidak ada deskripsi",
                        color=TEXT_MUTED,
                        size=11,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.icons.STAR_BORDER,
                                    size=12, color=TEXT_MUTED),
                            ft.Text(str(r.get("stars", 0)),
                                    size=11, color=TEXT_MUTED),
                            ft.Container(
                                width=1, height=10,
                                bgcolor=BORDER,
                                margin=ft.margin.symmetric(horizontal=6),
                            ),
                            ft.Text(
                                f"Diupdate: {r.get('updated_at', '-')}",
                                size=11, color=TEXT_MUTED,
                            ),
                        ],
                        spacing=2,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=BORDER),
                    ft.Column(
                        tight=True,
                        spacing=0,
                        controls=[
                            ft.Row(
                                [
                                    action_btn("Info",
                                               ft.icons.INFO_OUTLINE,
                                               ACCENT, self.on_info),
                                    action_btn("Update",
                                               ft.icons.SYNC,
                                               PRIMARY, self.on_upload),
                                ],
                                spacing=4,
                            ),
                            ft.Row(
                                [
                                    action_btn("Clone",
                                               ft.icons.DOWNLOAD_OUTLINED,
                                               ACCENT, self.on_clone),
                                ],
                                spacing=4,
                            ),
                            ft.Row(
                                [
                                    action_btn("Branch",
                                               ft.icons.ACCOUNT_TREE_OUTLINED,
                                               TEXT_MUTED, self.on_branches),
                                    action_btn("Settings",
                                               ft.icons.SETTINGS_OUTLINED,
                                               TEXT_MUTED, self.on_settings),
                                ],
                                spacing=4,
                            ),
                            ft.Row(
                                [
                                    action_btn("Hapus",
                                               ft.icons.DELETE_OUTLINE,
                                               DANGER, self.on_delete),
                                ],
                                spacing=4,
                            ),
                        ],
                    ),
                ],
            ),
        )
