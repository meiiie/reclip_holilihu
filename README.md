# HoLiLiHu ReClip

HoLiLiHu ReClip is a ReClip-based video/audio downloader with a clean web UI, bounded concurrent downloads, and MCP tools for Codex. Paste links from YouTube, TikTok, Instagram, Twitter/X, and 1000+ other sites — download as MP4 or MP3, or let Codex queue downloads for you.

This project is developed from the original [ReClip](https://github.com/averygan/reclip) project and keeps the MIT license.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

https://github.com/user-attachments/assets/419d3e50-c933-444b-8cab-a9724986ba05

![ReClip MP3 Mode](assets/preview-mp3.png)

## Features

- Download videos from 1000+ supported sites (via [yt-dlp](https://github.com/yt-dlp/yt-dlp))
- MP4 video or MP3 audio extraction
- Quality/resolution picker
- Bulk downloads with a bounded queue for stable concurrent downloads
- Automatic URL deduplication
- Clean, responsive UI — no frameworks, no build step
- Optional Codex MCP/plugin integration for agent-driven downloads

## Quick Start

```bash
brew install yt-dlp ffmpeg    # or apt install ffmpeg && pip install yt-dlp
git clone https://github.com/meiiie/reclip_holilihu.git
cd reclip_holilihu
./reclip.sh
```

Open **http://localhost:8899**.

Or with Docker:

```bash
docker build -t reclip . && docker run -p 8899:8899 reclip
```

## Usage

1. Paste one or more video URLs into the input box
2. Choose **MP4** (video) or **MP3** (audio)
3. Click **Fetch** to load video info and thumbnails
4. Select quality/resolution if available
5. Click **Download** on individual videos, or **Download All**

## Concurrent Downloads

HoLiLiHu ReClip uses a shared `DownloadManager` with a thread-safe job store and a bounded worker pool. The web UI can queue many links at once, while the backend limits how many videos are actively downloaded at the same time. Fragment concurrency is still delegated to yt-dlp through `concurrent_fragment_downloads`.

The defaults are:

- `max_concurrent_downloads`: 3 videos at a time
- `fragment_concurrency`: 4 fragments per video

You can change both from **Settings** in the app.

## Codex MCP / Plugin

This repo includes an MCP server so Codex can fetch metadata and download files directly:

```bash
python mcp_server.py
```

Recommended CLI setup after installing from GitHub:

```bash
pipx install git+https://github.com/meiiie/reclip_holilihu.git
reclip-holilihu setup-mcp codex
reclip-holilihu doctor
```

From a source checkout:

```bash
python reclip_holilihu_cli.py setup-mcp codex --source /absolute/path/to/reclip-holilihu
python reclip_holilihu_cli.py doctor
```

Direct Codex MCP setup is also supported:

```bash
codex mcp add holilihu-reclip -- python /absolute/path/to/reclip-holilihu/mcp_server.py
```

The repo also includes a local Codex plugin scaffold at `plugins/holilihu-reclip` and a marketplace file at `.agents/plugins/marketplace.json`. Treat the MCP server and CLI as the stable distribution path; use the repo-local plugin when your Codex build supports local plugin marketplaces.

For teammate handoff steps, see `docs/TEAMMATE_SETUP.md`. For publishing this fork as its own GitHub repository, see `docs/GITHUB_PUBLISH.md`.

After pushing this repo to GitHub, teammates can also install and configure Codex from PowerShell:

```powershell
iwr -UseBasicParsing -OutFile install_reclip_codex.ps1 https://raw.githubusercontent.com/meiiie/reclip_holilihu/main/scripts/install_reclip_codex.ps1
.\install_reclip_codex.ps1 -RepoUrl https://github.com/meiiie/reclip_holilihu.git
```

Available MCP tools:

- `get_video_info`
- `download_video`
- `download_many`
- `get_download_status`
- `get_runtime_status`
- `list_recent_downloads`

## Supported Sites

Anything [yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), including:

YouTube, TikTok, Instagram, Twitter/X, Reddit, Facebook, Vimeo, Twitch, Dailymotion, SoundCloud, Loom, Streamable, Pinterest, Tumblr, Threads, LinkedIn, and many more.

## Stack

- **Backend:** Python + Flask
- **Frontend:** Vanilla HTML/CSS/JS (single file, no build step)
- **Download engine:** [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [ffmpeg](https://ffmpeg.org/)
- **Agent integration:** Model Context Protocol Python SDK

## Disclaimer

This tool is intended for personal use only. Please respect copyright laws and the terms of service of the platforms you download from. The developers are not responsible for any misuse of this tool.

## License

HoLiLiHu ReClip is distributed under the [MIT License](LICENSE).

This project is developed from the original [ReClip](https://github.com/averygan/reclip) project. The original MIT license notice is preserved; see [NOTICE](NOTICE) for attribution.
