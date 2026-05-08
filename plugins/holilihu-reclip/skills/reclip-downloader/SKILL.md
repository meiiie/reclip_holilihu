---
name: reclip-downloader
description: Use HoLiLiHu ReClip MCP tools to fetch video metadata and download video or audio files into the local ReClip output folder.
---

# HoLiLiHu ReClip Downloader

Use this skill when the user asks Codex to download media URLs, fetch video metadata, batch-download links, or prepare local video/audio files for later editing.

## Workflow

1. Call `mcp__holilihu-reclip__get_runtime_status` first when reliability matters. Confirm ffmpeg is available before video downloads that need merge or audio conversion.
2. For one URL, call `mcp__holilihu-reclip__get_video_info` when the user needs title, duration, thumbnail, uploader, or quality choices.
3. Call `mcp__holilihu-reclip__download_video` for one URL. Use `media_type="video"` for MP4 and `media_type="audio"` for MP3. Set `wait=true` when the next step needs the finished local file path.
4. Call `mcp__holilihu-reclip__download_many` for batches. The ReClip manager enforces the configured parallel-download limit, so it is safe to queue many links.
5. Report the returned `file_path` values to the user. If a job is still queued or downloading, call `mcp__holilihu-reclip__get_download_status`.

Respect copyright law and platform terms. Download only content the user is allowed to access and use.
