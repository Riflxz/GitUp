# Fixed Bugs & Changelog

## v1.0.0 — Initial Release

Buggy prototype with threading issues and incomplete features.

---

## v1.0.1 — Threading Rewrite

### Fixed
- **White screen on page transitions** — All pages used `threading.Thread` for blocking API calls, causing race conditions with Flet's UI thread. Rewrote every page to use `asyncio.to_thread()` inside async event handlers.
- **`asyncio.ensure_future()` crash** — Flet 0.24.1 dispatches `on_click` via `ThreadPoolExecutor`, not the asyncio event loop. Calling `ensure_future()` from a thread-pool worker failed with "no running event loop". Replaced everywhere with `page.run_task()` which uses `asyncio.run_coroutine_threadsafe()` internally.
- **Rectangle blocks / broken rendering** — Caused by modifying Flet controls from background threads without synchronization.
- **Empty branch list** — Branch page loaded asynchronously but UI updated before data arrived, showing blank state permanently.
- **Missing Settings button on repo cards** — `repo_card.py` did not include the Settings action button.
- **`ft.Chip` API mismatch** — Used `on_deleted` but Flet 0.24.1 expects `on_delete`.
- **`git_ops.py` internal threading** — Clone/push functions created their own `threading.Thread`, causing race conditions. Made pure synchronous; callers use `asyncio.to_thread()`.
### Added
- `page.run_task()` pattern documented and applied across all pages.
- `main.py` stays synchronous (Flet 0.24.1 requirement).

---

## v1.0.2 — UX & Startup Improvements

### Fixed
- **Create repo success notification lost** — After creation, app navigated to dashboard immediately but the success message was set before repo list loaded, so it was overwritten. Fixed with `state.pending_success` — message stored in state, displayed as SnackBar after dashboard finishes loading repo list.
- **No feedback on create-repo completion** — User had no confirmation that the repo was created successfully.
### Added
- **Login auto-validation** — If token is saved in system keyring, auto-validate on startup without user interaction via `page.run_task(_auto_login)`.
- **`start.sh` multi-distro support** — Auto-detects Arch, Ubuntu, Fedora, openSUSE; finds Python 3.11+; creates venv; retries pip with `--break-system-packages` on PEP 668 errors.
- **libmpv symlink** — Auto-creates `libmpv.so.1` symlink from any `libmpv.so.*` found on the system.
- **tkinter check** — Warning if tkinter is missing for file dialogs.
- **Always `auto_init=True`** — Removed init-readme checkbox; guarantees a main branch exists, avoiding empty-repo edge cases.

---

## v1.0.3 — Info Page & Repository Management

### Fixed
- **Async handler not wrapped** — `_do_save_topics()` called `github_api.set_topics()` synchronously without `asyncio.to_thread()`, blocking the event loop.
- **Signatures mismatch** — `_open_topics_dialog(_)` took an argument but was called without one. Removed the unused parameter.
- **`is_topics_row` attribute missing** — `_refresh_topics_display()` checked `hasattr(c, '_topics_row')` but the container was never tagged. Fixed by setting `container.is_topics_row = True` in `_build_topics_row()`.
- **Create tag/release dialogs** — `_do_create` was `async def` passed directly as `on_click`. In Flet 0.24.1 this returns a coroutine without awaiting it. Wrapped with `page.run_task()`.
### Added
- **Info page** — New page (`pages/info_page.py`) showing full repository metadata.
- **URL rows with Open + Copy** — Each repo URL (GitHub, HTTPS clone) has a button to open in browser and a copy-to-clipboard button.
- **Topics management** — View, add, remove, and save GitHub topics via `replace_topics` API.
- **Tag management** — View tags, create new tags (with optional SHA), delete tags.
- **Release management** — View releases, create releases, delete releases (with confirmation dialog).
- **`github_api.py` additions** — `delete_tag()`, `delete_release()`, `set_topics()`, `get_default_branch_sha()`, `create_release()`.

---

## v1.0.4 — Cleanup & Polish

### Fixed
- **Window icon still showing gear** — `page.window.icon` needs base64-encoded PNG data URI, not a file path. Fixed with `data:image/png;base64,...` format using resized 64×64 icon.
- **`on_deleted` → `on_delete`** (missed one instance in info page).
- **Three separate scripts** — `start.sh`, `setup.sh`, `run.sh` merged into single `run.sh` with subcommands (`start`, `setup`, `check`, `help`).
### Added
- **Project logo** — `logo.png` (in-app), `icon.png` (window/taskbar).
- **`.gitignore`** — Excludes `venv/`, `__pycache__`, `.local-libs`, etc.
- **Author credit link** — `@ZeroXD909` in sidebar now blue (`ACCENT`) and clickable, opens `https://t.me/zeroxd909`.
- **`LICENSE`** — Cleaned up, removed cringey disclaimer footer.
- **`README.md`** — Updated with logo, info page in project structure, cleaned up.
- **Backup system** — Sanitized backups at `GitForge-v{version}/` (no venv, no pycache, no personal data).
