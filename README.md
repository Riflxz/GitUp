# GitHub Uploader

<div align="center">
  <img src="logo.png" alt="GitHub Uploader" width="128"/>
</div>

A cross-platform desktop GUI application for managing GitHub repositories — create, upload, clone, branch, and configure repositories with an intuitive interface.

<div align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/flet-0.24-green" alt="Flet">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/platform-linux-lightgrey" alt="Linux">
</div>

---

## Features

| Feature | Description |
|---------|-------------|
| **Authentication** | Secure login via GitHub Personal Access Token (PAT), persistent session with keyring |
| **Dashboard** | View all repositories with search, visibility filter (public/private), and sort options |
| **Create Repository** | Create repos with customizable `.gitignore` (searchable template picker) and custom license file upload |
| **Upload** | Upload folders or files to any repository with progress tracking |
| **Clone** | Clone repositories locally with branch selection |
| **Branch Management** | View, create, and delete branches |
| **Repository Settings** | Update visibility, description, features, and merge settings |
| **Info & Management** | View repo details, manage tags, releases, and topics |

## Screenshots

| Page | Description |
|------|-------------|
| **Login** | Token input form with real-time validation |
| **Dashboard** | Repository grid with search, filter, and sort |
| **Upload** | Folder/file selection with progress dialog |

## System Requirements

- **Operating System:** Linux (x86_64) — compatible with Arch Linux, Ubuntu, Debian, Fedora, openSUSE, and other major distributions
- **Python:** 3.11 or newer
- **Git:** Installed and available in `PATH`
- **GitHub PAT:** Personal Access Token with `repo` and `delete_repo` scopes

## Installation

### Automated Setup

```bash
git clone <repository-url>
cd github-uploader
bash setup.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Distribution-Specific Prerequisites

**Arch Linux:**
```bash
sudo pacman -S python python-pip git tk
```

**Ubuntu / Debian:**
```bash
sudo apt install python3 python3-pip python3-venv git python3-tk
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip git python3-tkinter
```

**openSUSE:**
```bash
sudo zypper install python3 python3-pip git python3-tk
```

## Running the Application

```bash
bash start.sh
```

Or manually:

```bash
source venv/bin/activate
python main.py
```

## Obtaining a GitHub Token

1. Go to [GitHub Token Settings](https://github.com/settings/tokens/new)
2. Select the following scopes:
   - **repo** — Full control of private repositories
   - **delete_repo** — Repository deletion
3. Click **Generate token**
4. Copy the token and paste it into the application login screen

> **Security:** Your token is stored securely using your system's keyring (via the `keyring` library). It is never exposed in plain text or shared.

## Project Structure

```
github-uploader/
├── main.py                  # Entry point & routing
├── config.py                # Global constants & theme colors
├── requirements.txt         # Python dependencies
├── setup.sh                 # Automated setup script
├── start.sh                 # Application launcher
├── core/
│   ├── auth.py              # Token management (keyring)
│   ├── file_dialog.py       # File picker (tkinter fallback)
│   ├── git_ops.py           # Git operations (clone, push)
│   ├── github_api.py        # PyGithub wrapper
│   └── state.py             # Global application state
├── pages/
│   ├── login_page.py        # Login screen
│   ├── dashboard_page.py    # Repository dashboard
│   ├── create_repo_page.py  # Repository creation
│   ├── upload_page.py       # File upload
│   ├── clone_page.py       # Repository cloning
│   ├── branch_page.py      # Branch management
│   ├── edit_repo_page.py   # Repository settings
│   └── info_page.py        # Repository info & release/tag management
└── components/
    ├── dialogs.py           # UI dialogs (error, success, confirm, progress)
    ├── file_item.py         # File item component
    ├── repo_card.py         # Repository card component
    └── sidebar.py           # Navigation sidebar
```

## Theme

The application uses a consistent **GitHub Dark** theme throughout all pages.

| Element | Color |
|---------|-------|
| Background | `#0D1117` |
| Surface / Card | `#161B22` |
| Input | `#21262D` |
| Border | `#30363D` |
| Primary (green) | `#238636` |
| Danger (red) | `#DA3633` |
| Main text | `#E6EDF3` |
| Muted text | `#8B949E` |
| Accent (blue) | `#58A6FF` |

## Technology Stack

| Technology | Version |
|------------|---------|
| [Python](https://www.python.org/) | 3.11+ |
| [Flet](https://flet.dev/) | 0.24 |
| [PyGithub](https://pygithub.readthedocs.io/) | 2.1 |
| [GitPython](https://gitpython.readthedocs.io/) | 3.1 |
| [keyring](https://github.com/jaraco/keyring) | 24.3 |

## License

This project is open source and distributed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
