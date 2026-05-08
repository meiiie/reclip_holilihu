import json as json_mod
import os
import subprocess as sp
import sys
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file

import history
import settings as app_settings
from downloader import COOKIES_FILE, compact_error, manager


def resource_path(relative_path):
    """Resolve bundled resources when running from PyInstaller."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static'),
)


def error_response(error, status=400):
    return jsonify({'error': compact_error(error)}), status


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json or {}
    try:
        return jsonify(manager.get_info(data.get('url', '')))
    except Exception as exc:
        return error_response(exc)


@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json or {}
    try:
        job = manager.start_download(
            url=data.get('url', ''),
            format_choice=data.get('format', 'video'),
            format_id=data.get('format_id'),
            title=data.get('title', ''),
            uploader=data.get('uploader', ''),
            duration=data.get('duration') or 0,
            thumbnail=data.get('thumbnail', ''),
            use_aac=data.get('use_aac'),
        )
        return jsonify({'job_id': job['job_id'], 'status': job['status']})
    except Exception as exc:
        return error_response(exc)


@app.route('/api/status/<job_id>')
def check_status(job_id):
    job = manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Không tìm thấy tác vụ'}), 404
    return jsonify({
        'status': job.get('status'),
        'error': job.get('error'),
        'filename': job.get('filename'),
        'file_path': job.get('file_path'),
        'progress': job.get('progress', 0),
        'speed': job.get('speed', ''),
        'eta': job.get('eta', ''),
        'created_at': job.get('created_at'),
        'started_at': job.get('started_at'),
        'completed_at': job.get('completed_at'),
    })


@app.route('/api/file/<job_id>')
def download_file(job_id):
    job = manager.get_job(job_id)
    if not job or job.get('status') != 'done':
        return jsonify({'error': 'File chưa sẵn sàng'}), 404
    return send_file(job['file_path'], as_attachment=True, download_name=job['filename'])


@app.route('/api/check')
def check_deps():
    manager.refresh_ffmpeg()
    return jsonify(manager.runtime_state())


@app.route('/api/jobs')
def get_jobs():
    return jsonify({'items': manager.list_jobs(), 'runtime': manager.runtime_state()})


@app.route('/api/history')
def get_history():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    try:
        limit = max(1, min(100, int(request.args.get('limit', 20))))
        offset = max(0, int(request.args.get('offset', 0)))
    except ValueError:
        return jsonify({'error': 'Tham số phân trang không hợp lệ'}), 400

    items, total = history.get_history(
        limit=limit,
        offset=offset,
        search=search,
        status_filter=status_filter,
    )
    stats = history.get_stats()
    return jsonify({'items': items, 'stats': stats, 'total': total, 'limit': limit, 'offset': offset})


@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    history.clear_history()
    return jsonify({'ok': True})


@app.route('/api/history/delete', methods=['POST'])
def delete_history_item():
    data = request.json or {}
    item_id = data.get('id')
    if item_id:
        history.delete_item(item_id)
    return jsonify({'ok': True})


@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    data = request.json or {}
    file_path = data.get('file_path', '')
    if file_path and os.path.isfile(file_path):
        sp.Popen(['explorer', '/select,', os.path.normpath(file_path)])
    elif file_path:
        folder = os.path.dirname(file_path)
        if os.path.isdir(folder):
            sp.Popen(['explorer', os.path.normpath(folder)])
    return jsonify({'ok': True})


@app.route('/api/settings')
def get_settings():
    return jsonify(app_settings.load_settings())


@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json or {}
    current = app_settings.load_settings()
    current.update(data)
    app_settings.save_settings(current)
    manager.reload_settings()
    return jsonify({'ok': True, 'settings': app_settings.load_settings()})


@app.route('/api/cookies', methods=['GET'])
def get_cookies_status():
    if os.path.isfile(COOKIES_FILE):
        mtime = datetime.fromtimestamp(os.path.getmtime(COOKIES_FILE)).strftime('%d/%m/%Y %H:%M')
        return jsonify({'has_cookies': True, 'message': f'Đã có cookies ({mtime})'})
    return jsonify({'has_cookies': False, 'message': 'Chưa có cookies'})


@app.route('/api/cookies', methods=['POST'])
def upload_cookies():
    data = request.json or {}
    content = data.get('content', '')
    if not content:
        return jsonify({'ok': False, 'error': 'File rỗng'})

    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

    try:
        parsed = json_mod.loads(content)
        cookies = parsed.get('cookies', parsed) if isinstance(parsed, dict) else parsed
        if isinstance(cookies, list) and cookies:
            count = 0
            with open(COOKIES_FILE, 'w', encoding='utf-8') as file:
                file.write('# Netscape HTTP Cookie File\n')
                for cookie in cookies:
                    domain = cookie.get('domain', '')
                    flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                    path = cookie.get('path', '/')
                    secure = 'TRUE' if cookie.get('secure') else 'FALSE'
                    expires = str(int(cookie.get('expirationDate', 0)))
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    file.write(f'{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n')
                    count += 1
            return jsonify({'ok': True, 'message': f'Đã chuyển đổi và lưu {count} cookies!'})
    except (json_mod.JSONDecodeError, TypeError, KeyError, ValueError):
        pass

    if '# ' in content or '\t' in content:
        with open(COOKIES_FILE, 'w', encoding='utf-8') as file:
            file.write(content)
        lines = [line for line in content.strip().split('\n') if line and not line.startswith('#')]
        return jsonify({'ok': True, 'message': f'Đã lưu {len(lines)} cookies!'})

    return jsonify({'ok': False, 'error': 'Không nhận dạng được định dạng file (cần .json hoặc .txt)'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8899))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(host=host, port=port, threaded=True)
