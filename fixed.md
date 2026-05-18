# Changelog

## v1.0.0 — Initial Release
Prototype awal dengan berbagai bug threading dan fitur belum lengkap.

## v1.0.1 — Threading Rewrite
- **Perbaikan:** White screen, rendering rusak, blank branch list, `asyncio.ensure_future()` crash — semua `threading.Thread` diganti `asyncio.to_thread()` + `page.run_task()`.
- **Perbaikan:** Missing Settings button di repo card.
- **Perbaikan:** `ft.Chip` API (`on_deleted` → `on_delete`).
- **Penambahan:** Pola `page.run_task()` diterapkan di semua halaman.

## v1.0.2 — UX & Startup
- **Perbaikan:** Notifikasi sukses create repo hilang — pakai `state.pending_success`.
- **Penambahan:** Login auto-validate via keyring.
- **Penambahan:** `start.sh` multi-distro, libmpv symlink, pip `--break-system-packages`.
- **Penambahan:** `auto_init=True` selalu aktif (hapus checkbox init readme).

## v1.0.3 — Info Page & Management
- **Penambahan:** Info page (metadata repo, URL open+copy, topics, tags, releases).
- **Penambahan:** API `delete_tag`, `delete_release`, `set_topics`.
- **Perbaikan:** Async handlers tanpa `page.run_task()` — `_do_save_topics`, `_do_create` dialog.

## v1.0.4 — Cleanup & Polish
- **Perbaikan:** Window icon (base64 data URI), `on_deleted` → `on_delete`.
- **Perbaikan:** `start.sh` + `setup.sh` + `run.sh` digabung jadi satu `run.sh` (start/setup/check/help).
- **Penambahan:** Logo aplikasi, `.gitignore`, author link `@ZeroXD909`.
- **Penambahan:** LICENSE & README dibersihkan.

## v1.1.0 — Rename & Script Merge
- **Perubahan:** Nama project `GitHub Uploader` → `GitForge`.
- **Perbaikan:** `run.sh` error `$PYTHON` undefined saat venv sudah ada.
- **Penambahan:** `fixed.md` changelog.
- **Penambahan:** Demo GIF, logo baru (in-app + window icon).

## v1.1.1 — File Manager
- **Penambahan:** File Manager di halaman Settings — browse, edit, dan hapus file/folder repository.
- **Penambahan:** API `get_contents`, `get_file_content`, `update_file`, `delete_file`.

## v1.2.0 — Editor Improvements
- **Perbaikan:** Edit dialog tembus layar — batasi tinggi editor (8–20 lines, max 360px).
- **Perbaikan:** Tombol Batal/Simpan nyatu dengan konten — padding + separator.
- **Penambahan:** Undo/Redo di editor file (stack per perubahan, debounce 0.3s).
- **Penambahan:** Tampilan editor ala VS Code (monospace, dark bg `#1E1E1E`, status bar).
