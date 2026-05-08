import time

from mcp.server.fastmcp import FastMCP

import history
from downloader import manager


mcp = FastMCP("holilihu-reclip")


def _metadata_for(url, enabled=True):
    if not enabled:
        return {}
    try:
        info = manager.get_info(url)
    except Exception:
        return {}
    return {
        'title': info.get('title', ''),
        'uploader': info.get('uploader', ''),
        'duration': info.get('duration') or 0,
        'thumbnail': info.get('thumbnail', ''),
    }


@mcp.tool()
def get_video_info(url: str) -> dict:
    """Return title, duration, uploader, thumbnail, and selectable video formats for one URL."""
    return manager.get_info(url)


@mcp.tool()
def download_video(
    url: str,
    media_type: str = 'video',
    format_id: str | None = None,
    use_aac: bool | None = None,
    wait: bool = True,
    timeout_seconds: int = 3600,
    fetch_info: bool = True,
) -> dict:
    """Queue one URL for download and optionally wait until the local file is ready."""
    metadata = _metadata_for(url, enabled=fetch_info)
    job = manager.start_download(
        url=url,
        format_choice=media_type,
        format_id=format_id,
        use_aac=use_aac,
        **metadata,
    )
    if wait:
        job = manager.wait_for_job(job['job_id'], timeout=timeout_seconds)
    return {'job': job}


@mcp.tool()
def download_many(
    urls: list[str],
    media_type: str = 'video',
    use_aac: bool | None = None,
    wait: bool = True,
    timeout_seconds: int = 7200,
    fetch_info: bool = True,
) -> dict:
    """Queue multiple URLs; the manager enforces the configured parallel-download limit."""
    started = []
    for url in urls:
        metadata = _metadata_for(url, enabled=fetch_info)
        started.append(manager.start_download(
            url=url,
            format_choice=media_type,
            use_aac=use_aac,
            **metadata,
        ))

    if not wait:
        return {'jobs': started, 'runtime': manager.runtime_state()}

    deadline = time.monotonic() + timeout_seconds
    finished = []
    for job in started:
        remaining = max(0, deadline - time.monotonic())
        finished.append(manager.wait_for_job(job['job_id'], timeout=remaining))

    return {'jobs': finished, 'runtime': manager.runtime_state()}


@mcp.tool()
def get_download_status(job_id: str) -> dict:
    """Return the current status for a queued or running download job."""
    job = manager.get_job(job_id)
    if not job:
        raise KeyError(f'Không tìm thấy tác vụ {job_id}')
    return job


@mcp.tool()
def get_runtime_status() -> dict:
    """Return ffmpeg, output folder, queue, and parallelism settings."""
    manager.refresh_ffmpeg()
    return manager.runtime_state()


@mcp.tool()
def list_recent_downloads(limit: int = 20) -> dict:
    """Return recent download history from HoLiLiHu ReClip."""
    safe_limit = max(1, min(100, int(limit)))
    items, total = history.get_history(limit=safe_limit, offset=0)
    return {'items': items, 'total': total, 'stats': history.get_stats()}


if __name__ == '__main__':
    mcp.run()
