# core/auth.py

import keyring
from config import KEYRING_SERVICE, KEYRING_KEY


def save_token(token: str) -> None:
    keyring.set_password(KEYRING_SERVICE, KEYRING_KEY, token)


def load_token() -> str:
    result = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY)
    return result if result else ""


def delete_token() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_KEY)
    except keyring.errors.PasswordDeleteError:
        pass


def validate_token(token: str) -> tuple[bool, dict]:
    from core.github_api import get_user_info

    if not token or not token.strip():
        return False, {"error": "Token tidak boleh kosong"}

    try:
        user_info = get_user_info(token.strip())
        return True, user_info
    except Exception as e:
        return False, {"error": str(e)}
