import os
import sys
import socket
import threading
import webbrowser
import webview

# Đặt GUI backend trước khi import webview platforms
if getattr(sys, 'frozen', False):
    os.environ['PYWEBVIEW_GUI'] = 'edgechromium'

from app import app


class Api:
    """JS API - gọi từ JavaScript qua window.pywebview.api"""

    def open_external(self, url):
        """Mở link trên trình duyệt mặc định."""
        webbrowser.open(url)


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_server(port):
    app.run(host='127.0.0.1', port=port, use_reloader=False, threaded=True)


if __name__ == '__main__':
    webview.settings['ALLOW_DOWNLOADS'] = True

    port = find_free_port()
    api = Api()

    server = threading.Thread(target=start_server, args=(port,), daemon=True)
    server.start()

    webview.create_window(
        'HoLiLiHu ReClip - Tải video miễn phí',
        f'http://127.0.0.1:{port}',
        width=900,
        height=750,
        min_size=(600, 500),
        text_select=True,
        js_api=api,
    )
    webview.start(
        debug=not getattr(sys, 'frozen', False),
        gui='edgechromium',
    )

    sys.exit(0)
