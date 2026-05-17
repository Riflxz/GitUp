# components/sidebar.py

import flet as ft
from config import (
    BG_SURFACE, BORDER, PRIMARY, DANGER,
    TEXT_MAIN, TEXT_MUTED, APP_NAME, APP_VERSION,
    PAGE_DASHBOARD, PAGE_CREATE
)


class Sidebar(ft.UserControl):
    def __init__(
        self,
        username: str,
        current_page: str,
        on_navigate: callable,
        on_logout: callable,
        avatar_url: str = "",
    ):
        super().__init__()
        self.username = username
        self.current_page = current_page
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.avatar_url = avatar_url

    def build(self):
        def nav_item(label, icon, page_name):
            is_active = self.current_page == page_name
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=18,
                                color=PRIMARY if is_active else TEXT_MUTED),
                        ft.Text(label, size=13,
                                color=TEXT_MAIN if is_active else TEXT_MUTED,
                                weight=ft.FontWeight.BOLD if is_active
                                       else ft.FontWeight.NORMAL),
                    ],
                    spacing=10,
                ),
                bgcolor=ft.colors.with_opacity(0.1, PRIMARY) if is_active
                        else ft.colors.TRANSPARENT,
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                border=ft.border.all(1, PRIMARY if is_active
                                     else ft.colors.TRANSPARENT),
                on_click=lambda _, p=page_name: self.on_navigate(p),
                ink=True,
            )

        return ft.Container(
            width=200,
            bgcolor=BG_SURFACE,
            border=ft.border.only(right=ft.BorderSide(1, BORDER)),
            padding=ft.padding.symmetric(vertical=20, horizontal=10),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.CircleAvatar(
                                    foreground_image_url=self.avatar_url or None,
                                    content=ft.Text(
                                        self.username[:2].upper(),
                                        color=TEXT_MAIN,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=PRIMARY,
                                    radius=22,
                                ),
                                ft.Text(
                                    self.username,
                                    color=TEXT_MAIN,
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "github.com",
                                    color=TEXT_MUTED, size=11,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=ft.padding.only(bottom=16),
                    ),

                    ft.Divider(height=1, color=BORDER),
                    ft.Container(height=8),

                    nav_item("Dashboard",     ft.icons.GRID_VIEW_OUTLINED,
                             PAGE_DASHBOARD),
                    nav_item("Buat Repository", ft.icons.ADD_CIRCLE_OUTLINE,
                             PAGE_CREATE),

                    ft.Container(expand=True),

                    ft.Divider(height=1, color=BORDER),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.LOGOUT, size=18, color=DANGER),
                                ft.Text("Logout", size=13, color=DANGER),
                            ],
                            spacing=10,
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                        border_radius=6,
                        on_click=lambda _: self.on_logout(),
                        ink=True,
                    ),
                    ft.Container(height=4),
                    ft.Text(
                        f"{APP_NAME} v{APP_VERSION}",
                        size=10,
                        color=TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "@ZeroXD909",
                        size=9,
                        color=TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                        opacity=0.6,
                    ),
                ],
                expand=True,
                spacing=4,
            ),
        )
