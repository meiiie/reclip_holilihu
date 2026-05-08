import glob
import os
import re
import shutil
import sys
import threading
import time
import unicodedata
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import yt_dlp

import history
import settings as app_settings


APP_HOME = os.path.join(os.path.expanduser('~'), '.holilihu_reclip')
COOKIES_FILE = os.path.join(APP_HOME, 'cookies.txt')
DEFAULT_MAX_CONCURRENT_DOWNLOADS = 3
DEFAULT_FRAGMENT_CONCURRENCY = 4
MAX_CONCURRENT_DOWNLOADS_LIMIT = 8
MAX_FRAGMENT_CONCURRENCY_LIMIT = 16


def clamp_int(value, default, low, high):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, parsed))


def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


def find_ffmpeg():
    exe_dir = get_exe_dir()

    if os.path.isfile(os.path.join(exe_dir, 'ffmpeg.exe')):
        return exe_dir

    ffmpeg_subdir = os.path.join(exe_dir, 'ffmpeg')
    if os.path.isfile(os.path.join(ffmpeg_subdir, 'ffmpeg.exe')):
        return ffmpeg_subdir

    if getattr(sys, 'frozen', False):
        bundle_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        if os.path.isfile(bundle_ffmpeg):
            return sys._MEIPASS

    ffmpeg_in_path = shutil.which('ffmpeg')
    if ffmpeg_in_path:
        return os.path.dirname(ffmpeg_in_path)

    for path in [
        r'C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin',
        r'C:\ffmpeg\bin',
        os.path.expanduser(r'~\scoop\shims'),
        r'C:\Program Files\ffmpeg\bin',
        r'C:\Program Files (x86)\ffmpeg\bin',
    ]:
        if os.path.isfile(os.path.join(path, 'ffmpeg.exe')):
            return path

    return None


def sanitize_filename(filename):
    filename = unicodedata.normalize('NFKC', filename or '')
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('._').strip()
    return filename[:150] if filename else 'untitled'


def compact_error(error):
    message = str(error)
    return message[:200] + '...' if len(message) > 200 else message


class DownloadManager:
    def __init__(self):
        self._lock = threading.RLock()
        self._jobs = {}
        self._futures = {}
        self._settings = {}
        self._download_dir = ''
        self._ffmpeg_dir = find_ffmpeg()
        self._max_workers = DEFAULT_MAX_CONCURRENT_DOWNLOADS
        self._fragment_concurrency = DEFAULT_FRAGMENT_CONCURRENCY
        self._executor = None
        self.reload_settings()

    def reload_settings(self):
        settings = app_settings.load_settings()
        output_path = settings.get('output_path') or app_settings.DEFAULTS['output_path']
        os.makedirs(output_path, exist_ok=True)
        max_workers = clamp_int(
            settings.get('max_concurrent_downloads'),
            DEFAULT_MAX_CONCURRENT_DOWNLOADS,
            1,
            MAX_CONCURRENT_DOWNLOADS_LIMIT,
        )
        fragment_concurrency = clamp_int(
            settings.get('fragment_concurrency'),
            DEFAULT_FRAGMENT_CONCURRENCY,
            1,
            MAX_FRAGMENT_CONCURRENCY_LIMIT,
        )

        with self._lock:
            self._settings = settings
            self._download_dir = output_path
            self._fragment_concurrency = fragment_concurrency
            if self._executor is None or max_workers != self._max_workers:
                old_executor = self._executor
                self._max_workers = max_workers
                self._executor = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix='reclip-download',
                )
                if old_executor is not None:
                    old_executor.shutdown(wait=False, cancel_futures=False)

    def refresh_ffmpeg(self):
        with self._lock:
            self._ffmpeg_dir = find_ffmpeg()
            return self._ffmpeg_dir

    def runtime_state(self):
        with self._lock:
            jobs = list(self._jobs.values())
            return {
                'ffmpeg': self._ffmpeg_dir is not None,
                'ffmpeg_path': self._ffmpeg_dir or '',
                'download_dir': self._download_dir,
                'max_concurrent_downloads': self._max_workers,
                'fragment_concurrency': self._fragment_concurrency,
                'queued': sum(1 for job in jobs if job.get('status') == 'queued'),
                'downloading': sum(1 for job in jobs if job.get('status') == 'downloading'),
                'total_jobs': len(jobs),
            }

    def get_job(self, job_id):
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def list_jobs(self):
        with self._lock:
            return [dict(job) for job in self._jobs.values()]

    def _set_job(self, job_id, **updates):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.update(updates)

    def _apply_yt_opts(self, opts):
        with self._lock:
            ffmpeg_dir = self._ffmpeg_dir
        if os.path.isfile(COOKIES_FILE):
            opts['cookiefile'] = COOKIES_FILE
        if ffmpeg_dir:
            opts['ffmpeg_location'] = ffmpeg_dir

    def _effective_download_dir(self, format_choice):
        with self._lock:
            base_dir = self._download_dir
            create_subfolders = self._settings.get('create_subfolders', True)
        if not create_subfolders:
            os.makedirs(base_dir, exist_ok=True)
            return base_dir

        media_dir = 'Audio' if format_choice == 'audio' else 'Videos'
        dated_dir = datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join(base_dir, media_dir, dated_dir)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _base_ydl_opts(self):
        with self._lock:
            fragment_concurrency = self._fragment_concurrency
        opts = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 10,
            'file_access_retries': 3,
            'fragment_retries': 10,
            'extractor_retries': 3,
            'continuedl': True,
            'concurrent_fragment_downloads': fragment_concurrency,
            'progress_delta': 0.5,
        }
        self._apply_yt_opts(opts)
        return opts

    def get_info(self, url):
        url = (url or '').strip()
        if not url:
            raise ValueError('Chưa nhập link')

        opts = self._base_ydl_opts()
        opts['simulate'] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        best_by_height = {}
        for item in info.get('formats', []):
            height = item.get('height')
            proto = item.get('protocol', '')
            if height and item.get('vcodec', 'none') != 'none' and 'm3u8' not in proto:
                bitrate = item.get('tbr') or 0
                current = best_by_height.get(height)
                if current is None or bitrate > (current.get('tbr') or 0):
                    best_by_height[height] = item

        formats = []
        for height, item in best_by_height.items():
            formats.append({
                'id': item['format_id'],
                'label': f'{height}p',
                'height': height,
            })
        formats.sort(key=lambda item: item['height'], reverse=True)

        return {
            'title': info.get('title', ''),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration'),
            'uploader': info.get('uploader', ''),
            'webpage_url': info.get('webpage_url') or url,
            'formats': formats,
        }

    def start_download(
        self,
        url,
        format_choice='video',
        format_id=None,
        title='',
        uploader='',
        duration=0,
        thumbnail='',
        use_aac=None,
    ):
        url = (url or '').strip()
        if not url:
            raise ValueError('Chưa nhập link')
        if format_choice not in ('video', 'audio'):
            raise ValueError('Định dạng tải không hợp lệ')

        with self._lock:
            use_default_aac = self._settings.get('use_aac', False)
            executor = self._executor

        if use_aac is None:
            use_aac = use_default_aac

        job_id = uuid.uuid4().hex[:10]
        job = {
            'job_id': job_id,
            'status': 'queued',
            'url': url,
            'format': format_choice,
            'format_id': format_id,
            'title': title or '',
            'uploader': uploader or '',
            'duration': duration or 0,
            'thumbnail': thumbnail or '',
            'use_aac': bool(use_aac),
            'progress': 0,
            'speed': '',
            'eta': '',
            'created_at': datetime.now().isoformat(),
        }

        with self._lock:
            self._jobs[job_id] = job
            future = executor.submit(
                self._run_download,
                job_id,
                url,
                format_choice,
                format_id,
                bool(use_aac),
            )
            self._futures[job_id] = future
            future.add_done_callback(lambda completed, jid=job_id: self._finalize_future(jid, completed))

        return dict(job)

    def _finalize_future(self, job_id, future):
        try:
            error = future.exception()
        except Exception as exc:
            error = exc
        if error:
            job = self.get_job(job_id)
            if job and job.get('status') not in ('done', 'error'):
                self._set_job(job_id, status='error', error=compact_error(error))
        with self._lock:
            self._futures.pop(job_id, None)

    def _run_download(self, job_id, url, format_choice, format_id, use_aac):
        output_dir = self._effective_download_dir(format_choice)
        out_template = os.path.join(output_dir, f'{job_id}.%(ext)s')
        self._set_job(job_id, status='downloading', started_at=datetime.now().isoformat())

        def progress_hook(payload):
            status = payload.get('status')
            if status == 'downloading':
                total = payload.get('total_bytes') or payload.get('total_bytes_estimate') or 0
                downloaded = payload.get('downloaded_bytes', 0)
                updates = {}
                if total > 0:
                    updates['progress'] = round((downloaded / total) * 100, 1)
                speed = payload.get('speed')
                if speed:
                    if speed >= 1024 * 1024:
                        updates['speed'] = f'{speed / 1024 / 1024:.1f} MB/s'
                    else:
                        updates['speed'] = f'{speed / 1024:.0f} KB/s'
                eta = payload.get('eta')
                if eta is not None:
                    updates['eta'] = f'{eta}s'
                if updates:
                    self._set_job(job_id, **updates)
            elif status == 'finished':
                self._set_job(job_id, progress=100, speed='', eta='')

        opts = self._base_ydl_opts()
        opts.update({
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
        })

        if format_choice == 'audio':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        elif format_id:
            opts['format'] = f'{format_id}+bestaudio/best'
            opts['merge_output_format'] = 'mp4'
        else:
            opts['format'] = 'bestvideo+bestaudio/best'
            opts['merge_output_format'] = 'mp4'

        if use_aac and format_choice != 'audio':
            opts['postprocessor_args'] = {'merger': ['-c:a', 'aac', '-b:a', '192k']}

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            files = glob.glob(os.path.join(output_dir, f'{job_id}.*'))
            if not files:
                raise RuntimeError('Tải xong nhưng không tìm thấy file')

            expected_ext = '.mp3' if format_choice == 'audio' else '.mp4'
            targets = [path for path in files if path.lower().endswith(expected_ext)]
            chosen = targets[0] if targets else files[0]

            for path in files:
                if path != chosen:
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            job = self.get_job(job_id) or {}
            ext = os.path.splitext(chosen)[1]
            title = job.get('title', '').strip()
            filename = f'{sanitize_filename(title)}{ext}' if title else os.path.basename(chosen)
            file_size = os.path.getsize(chosen) if os.path.isfile(chosen) else 0

            self._set_job(
                job_id,
                status='done',
                file=chosen,
                file_path=chosen,
                filename=filename,
                file_size=file_size,
                progress=100,
                speed='',
                eta='',
                completed_at=datetime.now().isoformat(),
            )

            history.add_download(
                url=url,
                title=job.get('title', ''),
                uploader=job.get('uploader', ''),
                download_type=format_choice,
                quality=format_id or 'best',
                file_path=chosen,
                file_size=file_size,
                duration=job.get('duration', 0),
                thumbnail=job.get('thumbnail', ''),
                status='completed',
            )
        except Exception as exc:
            message = compact_error(exc)
            with self._lock:
                ffmpeg_missing = self._ffmpeg_dir is None
            if 'ffmpeg' in message.lower() and ffmpeg_missing:
                message = 'Cần ffmpeg để ghép video+audio. Đặt ffmpeg.exe cạnh file .exe'
            self._set_job(
                job_id,
                status='error',
                error=message,
                completed_at=datetime.now().isoformat(),
            )
            job = self.get_job(job_id) or {}
            history.add_download(
                url=url,
                title=job.get('title', ''),
                download_type=format_choice,
                status='error',
                error_message=message,
            )

    def wait_for_job(self, job_id, timeout=None, poll_interval=0.5):
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            job = self.get_job(job_id)
            if not job:
                raise KeyError(f'Không tìm thấy tác vụ {job_id}')
            if job.get('status') in ('done', 'error'):
                return job
            if deadline is not None and time.monotonic() >= deadline:
                return job
            time.sleep(poll_interval)

    def download_and_wait(self, timeout=None, **kwargs):
        job = self.start_download(**kwargs)
        return self.wait_for_job(job['job_id'], timeout=timeout)


manager = DownloadManager()
