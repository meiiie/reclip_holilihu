# Publish HoLiLiHu ReClip to GitHub

This project started from the original ReClip repository. To publish HoLiLiHu ReClip as its own GitHub project, keep the original repository as `upstream` and use your HoLiLiHu repository as `origin`.

## 1. Create the GitHub repository

Create a new empty repository on GitHub:

```text
meiiie/reclip-holilihu-mcp
```

Recommended settings:

- Visibility: private while stabilizing, public when ready
- License: MIT
- Description: `HoLiLiHu ReClip video downloader with Codex MCP tools`
- Topics: `mcp`, `codex`, `yt-dlp`, `video-downloader`, `flask`

Do not initialize the GitHub repository with a README, license, or `.gitignore` because this local repo already has them.

## 2. Rewire remotes

Current local `origin` points to the original ReClip repo. Rename it to `upstream`:

```bash
git remote rename origin upstream
git remote add origin https://github.com/meiiie/reclip-holilihu-mcp.git
git remote -v
```

Expected shape:

```text
origin    https://github.com/meiiie/reclip-holilihu-mcp.git (fetch)
origin    https://github.com/meiiie/reclip-holilihu-mcp.git (push)
upstream  https://github.com/averygan/reclip.git (fetch)
upstream  https://github.com/averygan/reclip.git (push)
```

## 3. Commit the HoLiLiHu changes

Review files first:

```bash
git status --short
git diff --stat
```

Stage source, docs, plugin, workflow, and packaging files:

```bash
git add .gitignore README.md requirements.txt requirements-desktop.txt pyproject.toml
git add app.py downloader.py mcp_server.py reclip_holilihu_cli.py settings.py history.py desktop.py
git add templates static assets/app.ico app.manifest ReClip.spec version_info.txt
git add plugins .agents docs scripts .github
git add create_installer.py installer_stub.py installer.iss
```

Do not stage generated outputs:

```text
.venv/
build/
dist/
downloads/
*.exe
*.rar
__pycache__/
```

Commit:

```bash
git commit -m "Create HoLiLiHu ReClip MCP edition"
```

## 4. Push

```bash
git branch -M main
git push -u origin main
```

## 5. Create a release

Tag the first release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Actions workflow builds the Windows setup artifact on tag push.

## 6. Teammate install commands

Codex/MCP users:

```powershell
pipx install git+https://github.com/meiiie/reclip-holilihu-mcp.git
reclip-holilihu-mcp setup-mcp codex
reclip-holilihu-mcp doctor
```

Source checkout users:

```powershell
iwr -UseBasicParsing -OutFile install_reclip_codex.ps1 https://raw.githubusercontent.com/meiiie/reclip-holilihu-mcp/main/scripts/install_reclip_codex.ps1
.\install_reclip_codex.ps1 -RepoUrl https://github.com/meiiie/reclip-holilihu-mcp.git
```

Desktop users:

```text
Download HoLiLiHu-ReClip-Setup.exe from GitHub Releases.
```

## 7. Keeping original ReClip updates available

Fetch original ReClip when you need to compare or merge upstream changes:

```bash
git fetch upstream
git log --oneline main..upstream/main
```

Only merge upstream intentionally after checking whether the changes still fit HoLiLiHu ReClip.

