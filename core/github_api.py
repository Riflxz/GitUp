# core/github_api.py

from github import Github, GithubException, BadCredentialsException, UnknownObjectException


def _client(token: str) -> Github:
    return Github(token)


# ── User ─────────────────────────────────────────────────────────

def get_user_info(token: str) -> dict:
    try:
        g = _client(token)
        u = g.get_user()
        return {
            "login":        u.login,
            "avatar_url":   u.avatar_url,
            "name":         u.name or u.login,
            "public_repos": u.public_repos,
        }
    except BadCredentialsException:
        raise Exception("Token tidak valid atau sudah kedaluwarsa")
    except Exception as e:
        raise Exception(f"Gagal terhubung ke GitHub: {e}")


# ── Repository ───────────────────────────────────────────────────

def get_repos(token: str) -> list[dict]:
    try:
        g = _client(token)
        user = g.get_user()
        repos = []
        for r in user.get_repos(sort="updated", direction="desc"):
            repos.append({
                "name":           r.name,
                "full_name":      r.full_name,
                "private":        r.private,
                "description":    r.description or "",
                "html_url":       r.html_url,
                "default_branch": r.default_branch,
                "updated_at":     r.updated_at.strftime("%d %b %Y") if r.updated_at else "-",
                "stars":          r.stargazers_count,
            })
        return repos
    except Exception as e:
        raise Exception(f"Gagal memuat daftar repository: {e}")


def create_repo(
    token: str,
    name: str,
    description: str,
    private: bool,
    gitignore_template: str,
    license_template: str,
) -> dict:
    try:
        g = _client(token)
        user = g.get_user()
        kwargs = {
            "name":        name,
            "description": description,
            "private":     private,
            "auto_init":   True,
        }
        if gitignore_template:
            kwargs["gitignore_template"] = gitignore_template
        if license_template:
            kwargs["license_template"] = license_template

        r = user.create_repo(**kwargs)
        return {
            "name":           r.name,
            "full_name":      r.full_name,
            "private":        r.private,
            "description":    r.description or "",
            "html_url":       r.html_url,
            "default_branch": r.default_branch,
            "updated_at":     r.updated_at.strftime("%d %b %Y") if r.updated_at else "-",
            "stars":          0,
        }
    except GithubException as e:
        msg = e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)
        raise Exception(f"Gagal membuat repository: {msg}")


def get_repo_detail(token: str, full_name: str) -> dict:
    try:
        g = _client(token)
        r = g.get_repo(full_name)
        return {
            "name":                 r.name,
            "full_name":            r.full_name,
            "private":              r.private,
            "description":          r.description or "",
            "homepage":             r.homepage or "",
            "default_branch":       r.default_branch,
            "has_issues":           r.has_issues,
            "has_projects":         r.has_projects,
            "has_wiki":             r.has_wiki,
            "allow_squash_merge":   r.allow_squash_merge,
            "allow_merge_commit":   r.allow_merge_commit,
            "allow_rebase_merge":   r.allow_rebase_merge,
            "delete_branch_on_merge": r.delete_branch_on_merge,
            "archived":             r.archived,
            "html_url":             r.html_url,
            "updated_at":           r.updated_at.strftime("%d %b %Y") if r.updated_at else "-",
        }
    except Exception as e:
        raise Exception(f"Gagal memuat detail repository: {e}")


def update_repo(token: str, full_name: str, **kwargs) -> dict:
    try:
        g = _client(token)
        r = g.get_repo(full_name)
        r.edit(**kwargs)
        return get_repo_detail(token, full_name)
    except GithubException as e:
        msg = e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)
        raise Exception(f"Gagal memperbarui repository: {msg}")
    except Exception as e:
        raise Exception(f"Gagal memperbarui repository: {e}")


def delete_repo(token: str, full_name: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        repo.delete()
        return True
    except Exception as e:
        raise Exception(f"Gagal menghapus repository: {e}")


# ── Branches ─────────────────────────────────────────────────────

def get_branches(token: str, full_name: str) -> list[str]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        return [b.name for b in repo.get_branches()]
    except Exception as e:
        raise Exception(f"Gagal memuat branch: {e}")


def create_branch(token: str, full_name: str, new_branch: str, from_branch: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        source = repo.get_branch(from_branch)
        repo.create_git_ref(
            ref=f"refs/heads/{new_branch}",
            sha=source.commit.sha,
        )
        return True
    except Exception as e:
        raise Exception(f"Gagal membuat branch '{new_branch}': {e}")


def delete_branch(token: str, full_name: str, branch: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        ref = repo.get_git_ref(f"heads/{branch}")
        ref.delete()
        return True
    except Exception as e:
        raise Exception(f"Gagal menghapus branch '{branch}': {e}")


# ── Templates ────────────────────────────────────────────────────

# ── File Upload ──────────────────────────────────────────────────

def upload_file_to_repo(
    token: str,
    full_name: str,
    file_path: str,
    target_path: str,
    branch: str = "main",
    message: str = None,
) -> dict:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        with open(file_path, "rb") as f:
            content = f.read()
        msg = message or f"Add {target_path}"
        result = repo.create_file(target_path, msg, content, branch=branch)
        return result
    except Exception as e:
        raise Exception(f"Gagal mengupload file: {e}")


def get_gitignore_templates(token: str) -> list[str]:
    try:
        g = _client(token)
        return list(g.get_gitignore_templates())
    except Exception:
        return ["Python", "Node", "Java", "Go", "Rust", "C++", "Unity", "Android"]


# ── Full Repo Info ───────────────────────────────────────────────

def get_full_repo_info(token: str, full_name: str) -> dict:
    try:
        g = _client(token)
        r = g.get_repo(full_name)
        return {
            "name":           r.name,
            "full_name":      r.full_name,
            "private":        r.private,
            "description":    r.description or "",
            "html_url":       r.html_url,
            "clone_url":      r.clone_url,
            "ssh_url":        r.ssh_url,
            "default_branch": r.default_branch,
            "language":       r.language or "",
            "topics":         r.get_topics() if hasattr(r, "get_topics") else [],
            "stars":          r.stargazers_count,
            "forks":          r.forks_count,
            "open_issues":    r.open_issues_count,
            "created_at":     r.created_at.strftime("%d %b %Y") if r.created_at else "-",
            "updated_at":     r.updated_at.strftime("%d %b %Y") if r.updated_at else "-",
        }
    except Exception as e:
        raise Exception(f"Gagal memuat info repository: {e}")


# ── Tags ─────────────────────────────────────────────────────────

def get_tags(token: str, full_name: str) -> list[dict]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        return [
            {
                "name": t.name,
                "sha":  t.commit.sha,
            }
            for t in repo.get_tags()
        ]
    except Exception as e:
        raise Exception(f"Gagal memuat tags: {e}")


def create_tag(token: str, full_name: str, tag_name: str, sha: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        repo.create_git_ref(f"refs/tags/{tag_name}", sha)
        return True
    except Exception as e:
        raise Exception(f"Gagal membuat tag '{tag_name}': {e}")


def delete_tag(token: str, full_name: str, tag_name: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        ref = repo.get_git_ref(f"tags/{tag_name}")
        ref.delete()
        return True
    except Exception as e:
        raise Exception(f"Gagal menghapus tag '{tag_name}': {e}")


# ── Topics ───────────────────────────────────────────────────────

def get_topics(token: str, full_name: str) -> list[str]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        return repo.get_topics()
    except Exception as e:
        raise Exception(f"Gagal memuat topics: {e}")


def set_topics(token: str, full_name: str, topics: list[str]) -> list[str]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        return repo.replace_topics(topics)
    except Exception as e:
        raise Exception(f"Gagal menyimpan topics: {e}")


# ── Releases ─────────────────────────────────────────────────────

def get_releases(token: str, full_name: str) -> list[dict]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        return [
            {
                "id":          rel.id,
                "tag_name":    rel.tag_name,
                "title":       rel.title or "",
                "body":        rel.body or "",
                "published_at": rel.published_at.strftime("%d %b %Y") if rel.published_at else "-",
                "html_url":    rel.html_url,
                "draft":       rel.draft,
                "prerelease":  rel.prerelease,
            }
            for rel in repo.get_releases()
        ]
    except Exception as e:
        raise Exception(f"Gagal memuat releases: {e}")


def create_release(token: str, full_name: str, tag: str, title: str, body: str, draft: bool = False, prerelease: bool = False) -> dict:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        rel = repo.create_git_release(tag, title, body, draft=draft, prerelease=prerelease)
        return {
            "tag_name":     rel.tag_name,
            "title":        rel.title or "",
            "body":         rel.body or "",
            "published_at": rel.published_at.strftime("%d %b %Y") if rel.published_at else "-",
            "html_url":     rel.html_url,
        }
    except Exception as e:
        raise Exception(f"Gagal membuat release: {e}")


def delete_release(token: str, full_name: str, tag_name: str) -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        for rel in repo.get_releases():
            if rel.tag_name == tag_name:
                rel.delete_release()
                return True
        raise Exception(f"Release dengan tag '{tag_name}' tidak ditemukan")
    except Exception as e:
        raise Exception(f"Gagal menghapus release: {e}")


def update_release(token: str, full_name: str, tag_name: str, title: str, body: str, draft: bool = False, prerelease: bool = False) -> dict:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        for rel in repo.get_releases():
            if rel.tag_name == tag_name:
                rel.update_release(title, body, draft=draft, prerelease=prerelease)
                return {
                    "tag_name":     rel.tag_name,
                    "title":        rel.title or "",
                    "body":         rel.body or "",
                    "published_at": rel.published_at.strftime("%d %b %Y") if rel.published_at else "-",
                    "html_url":     rel.html_url,
                    "draft":        rel.draft,
                    "prerelease":   rel.prerelease,
                }
        raise Exception(f"Release dengan tag '{tag_name}' tidak ditemukan")
    except Exception as e:
        raise Exception(f"Gagal memperbarui release: {e}")


# ── File Manager ─────────────────────────────────────────────

def get_contents(token: str, full_name: str, path: str = "") -> list[dict]:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        contents = repo.get_contents(path)
        if not isinstance(contents, list):
            contents = [contents]
        return [
            {
                "name": c.name,
                "path": c.path,
                "type": "dir" if c.type == "dir" else "file",
                "size": c.size,
                "sha":  c.sha,
                "download_url": c.download_url if c.type == "file" else "",
            }
            for c in contents
        ]
    except Exception as e:
        raise Exception(f"Gagal memuat konten: {e}")


def get_file_content(token: str, full_name: str, path: str) -> dict:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        c = repo.get_contents(path)
        return {
            "name": c.name,
            "path": c.path,
            "sha":  c.sha,
            "size": c.size,
            "content": c.decoded_content.decode("utf-8", errors="replace"),
        }
    except Exception as e:
        raise Exception(f"Gagal membaca file: {e}")


def update_file(token: str, full_name: str, path: str,
                content: str, message: str, sha: str,
                branch: str = "") -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        kwargs = {"branch": branch} if branch else {}
        repo.update_file(path, message, content, sha, **kwargs)
        return True
    except Exception as e:
        raise Exception(f"Gagal memperbarui file: {e}")


def delete_file(token: str, full_name: str, path: str,
                message: str, sha: str, branch: str = "") -> bool:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        kwargs = {"branch": branch} if branch else {}
        repo.delete_file(path, message, sha, **kwargs)
        return True
    except Exception as e:
        raise Exception(f"Gagal menghapus file: {e}")


def get_default_branch_sha(token: str, full_name: str) -> str:
    try:
        g = _client(token)
        repo = g.get_repo(full_name)
        branch = repo.get_branch(repo.default_branch)
        return branch.commit.sha
    except Exception as e:
        raise Exception(f"Gagal mengambil SHA branch: {e}")
