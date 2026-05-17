# core/state.py — State global aplikasi (satu instance, di-pass ke semua halaman)

class AppState:
    def __init__(self):
        self.token: str = ""
        self.username: str = ""
        self.user_display: str = ""
        self.avatar_url: str = ""
        self.repos: list = []
        self.selected_repo: dict = {}
        self.current_page: str = "login"
        self.pending_success: str | None = None
