# HoLiLiHu ReClip - teammate setup

This guide is for sending HoLiLiHu ReClip to teammates as a local app plus Codex MCP/plugin tooling.

## What to send

Recommended for teammates who use Codex:

1. Push this repository to GitHub.
2. Ask teammates to run the GitHub install script below.
3. Do not commit `.venv/`, `build/`, `dist/`, `downloads/`, or temporary installer output unless you are publishing a finished release artifact.

Recommended for non-technical teammates:

1. Create a GitHub tag like `v1.0.0`.
2. Let GitHub Actions build `HoLiLiHu-ReClip-Setup.exe`.
3. Send teammates the GitHub Release link.

## Install from GitHub and configure Codex

Preferred CLI setup:

```powershell
pipx install git+https://github.com/meiiie/reclip-holilihu-mcp.git
reclip-holilihu-mcp setup-mcp codex
reclip-holilihu-mcp doctor
```

The CLI setup mirrors larger MCP projects: install a small command-line tool, ask it to write the AI-agent MCP configuration, then run a diagnostic command.

If teammates do not have `pipx`, they can use the source install scripts below.

Windows PowerShell:

```powershell
iwr -UseBasicParsing -OutFile install_reclip_codex.ps1 https://raw.githubusercontent.com/meiiie/reclip-holilihu-mcp/main/scripts/install_reclip_codex.ps1
.\install_reclip_codex.ps1 -RepoUrl https://github.com/meiiie/reclip-holilihu-mcp.git
```

macOS/Linux:

```bash
curl -fsSL -o install_reclip_codex.sh https://raw.githubusercontent.com/meiiie/reclip-holilihu-mcp/main/scripts/install_reclip_codex.sh
bash install_reclip_codex.sh --repo-url https://github.com/meiiie/reclip-holilihu-mcp.git
```

The installer script will:

- Clone or update the repo into a local install directory.
- Create `.venv`.
- Install `requirements.txt`.
- Add or replace the `reclip-holilihu-mcp` MCP block in Codex config.
- Print the app and MCP paths.

Restart Codex after running the script so it reloads MCP tools.

## App setup from source

Requirements:

- Python 3.10 or newer
- ffmpeg available on `PATH`, or `ffmpeg.exe` placed beside the packaged `.exe`

Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Open:

```text
http://127.0.0.1:8899
```

If port `8899` is busy:

```powershell
$env:PORT="8900"
.venv\Scripts\python.exe app.py
```

## Codex MCP setup

The CLI writes this Codex MCP block automatically. Manual setup is useful for debugging or for teammates who do not want to install the CLI.

Windows example:

```powershell
codex mcp add reclip-holilihu-mcp -- E:\path\to\reclip-holilihu-mcp\.venv\Scripts\python.exe E:\path\to\reclip-holilihu-mcp\mcp_server.py
```

Equivalent `~/.codex/config.toml` entry:

```toml
[mcp_servers.reclip-holilihu-mcp]
command = "E:\\path\\to\\reclip-holilihu-mcp\\.venv\\Scripts\\python.exe"
args = ["E:\\path\\to\\reclip-holilihu-mcp\\mcp_server.py"]
cwd = "E:\\path\\to\\reclip-holilihu-mcp"
startup_timeout_sec = 20
tool_timeout_sec = 7200
```

Available MCP tools:

- `get_video_info`
- `download_video`
- `download_many`
- `get_download_status`
- `get_runtime_status`
- `list_recent_downloads`

## Codex plugin setup

This repo also includes a repo-local plugin at:

```text
plugins/reclip-holilihu-mcp
```

The plugin provides:

- `.codex-plugin/plugin.json` metadata
- `.mcp.json` that launches the ReClip MCP wrapper
- `skills/reclip-downloader/SKILL.md` so Codex knows when and how to use the MCP tools

For teammates, add this repo as a local marketplace in Codex, then install **HoLiLiHu ReClip** from the plugin UI. If plugin loading is not available in their Codex build, use the CLI or direct MCP setup above.

## Publishing to your own GitHub repo

This project currently has `origin` pointing at the original ReClip repository. For a HoLiLiHu repo, use the original project as upstream and make your GitHub repository the new origin:

```bash
git remote rename origin upstream
git remote add origin https://github.com/meiiie/reclip-holilihu-mcp.git
git branch -M main
git push -u origin main
```

Recommended repository settings:

- Name: `reclip-holilihu-mcp`
- Description: `HoLiLiHu ReClip video downloader with Codex MCP tools`
- License: MIT
- Topics: `mcp`, `codex`, `yt-dlp`, `video-downloader`, `flask`

After the first push:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The tag triggers the Windows release workflow and publishes the setup artifact.

## Operational notes

- Default max active downloads: `3`
- Default fragment concurrency per video: `4`
- Both can be changed from the app Settings tab.
- Cookies are stored locally at `~/.holilihu_reclip/cookies.txt`.
- History and settings are stored locally under `~/.holilihu_reclip`.

Respect copyright law and platform terms. Only download content the team is allowed to access and use.

