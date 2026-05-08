"""Quản lý lịch sử tải xuống - SQLite."""
import os
import sqlite3
import threading
from datetime import datetime


def get_db_path():
    """Đường dẫn database lịch sử."""
    app_dir = os.path.join(os.path.expanduser('~'), '.holilihu_reclip')
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, 'history.db')


_db_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(get_db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Tạo bảng lịch sử nếu chưa có."""
    with _db_lock:
        conn = _get_conn()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT DEFAULT '',
                uploader TEXT DEFAULT '',
                download_type TEXT DEFAULT 'video',
                quality TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                file_size INTEGER DEFAULT 0,
                duration INTEGER DEFAULT 0,
                thumbnail TEXT DEFAULT '',
                status TEXT DEFAULT 'completed',
                downloaded_at TEXT NOT NULL,
                error_message TEXT DEFAULT ''
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_downloaded_at ON downloads(downloaded_at)')
        conn.commit()
        conn.close()


def add_download(url, title='', uploader='', download_type='video', quality='',
                 file_path='', file_size=0, duration=0, thumbnail='',
                 status='completed', error_message=''):
    """Thêm bản ghi lịch sử."""
    with _db_lock:
        conn = _get_conn()
        conn.execute('''
            INSERT INTO downloads
            (url, title, uploader, download_type, quality, file_path, file_size,
             duration, thumbnail, status, downloaded_at, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, title, uploader, download_type, quality, file_path, file_size,
              duration, thumbnail, status, datetime.now().isoformat(), error_message))
        conn.commit()
        conn.close()


def get_history(limit=20, offset=0, search='', status_filter=''):
    """Lấy lịch sử tải kèm tổng số bản ghi."""
    with _db_lock:
        conn = _get_conn()
        where = ' WHERE 1=1'
        params = []

        if search:
            where += ' AND (title LIKE ? OR uploader LIKE ? OR url LIKE ?)'
            s = f'%{search}%'
            params.extend([s, s, s])

        if status_filter:
            where += ' AND status = ?'
            params.append(status_filter)

        # Đếm tổng
        total = conn.execute('SELECT COUNT(*) FROM downloads' + where, params).fetchone()[0]

        # Lấy trang
        query = 'SELECT * FROM downloads' + where + ' ORDER BY downloaded_at DESC LIMIT ? OFFSET ?'
        rows = conn.execute(query, params + [limit, offset]).fetchall()
        conn.close()
        return [dict(r) for r in rows], total


def get_stats():
    """Thống kê tổng quan."""
    with _db_lock:
        conn = _get_conn()
        stats = {}
        stats['total'] = conn.execute('SELECT COUNT(*) FROM downloads').fetchone()[0]
        stats['completed'] = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE status='completed'").fetchone()[0]
        stats['errors'] = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE status='error'").fetchone()[0]
        size_row = conn.execute(
            "SELECT COALESCE(SUM(file_size), 0) FROM downloads WHERE status='completed'"
        ).fetchone()
        stats['total_size_mb'] = round(size_row[0] / (1024 * 1024), 1) if size_row[0] else 0
        conn.close()
        return stats


def delete_item(item_id):
    """Xóa 1 mục lịch sử."""
    with _db_lock:
        conn = _get_conn()
        conn.execute('DELETE FROM downloads WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()


def clear_history():
    """Xóa toàn bộ lịch sử."""
    with _db_lock:
        conn = _get_conn()
        conn.execute('DELETE FROM downloads')
        conn.commit()
        conn.close()


# Khởi tạo DB khi import
init_db()
