# -*- mode: python ; coding: utf-8 -*-
# ReClip.spec - Cấu hình build chuyên nghiệp

import os
import importlib

block_cipher = None
PROJECT_ROOT = os.path.abspath(SPECPATH)

# Tìm đường dẫn pywebview lib để bundle
webview_pkg = os.path.dirname(importlib.import_module('webview').__file__)

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'desktop.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, 'templates'), 'templates'),
        (os.path.join(PROJECT_ROOT, 'static'), 'static'),
        (os.path.join(webview_pkg, 'lib'), os.path.join('webview', 'lib')),
    ],
    hiddenimports=[
        # Flask
        'flask', 'jinja2', 'jinja2.ext', 'markupsafe',
        'itsdangerous', 'click', 'blinker',
        'werkzeug', 'werkzeug.serving',
        # pywebview
        'webview', 'webview.platforms.edgechromium',
        'webview.platforms.winforms',
        'clr_loader', 'pythonnet',
        # yt-dlp
        'yt_dlp',
        # app modules
        'app', 'downloader', 'history', 'settings',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', '_tkinter', 'unittest', 'pydoc', 'doctest',
        'pdb', 'profile', 'pstats',
        'test', 'lib2to3', 'idlelib', 'turtledemo',
        'numpy', 'pandas', 'matplotlib', 'scipy',
        'IPython', 'notebook', 'pytest', 'PIL',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HoLiLiHu-ReClip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python3.dll',
        'api-ms-win-*.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=os.path.join(PROJECT_ROOT, 'version_info.txt'),
    icon=os.path.join(PROJECT_ROOT, 'assets', 'app.ico'),
    manifest=os.path.join(PROJECT_ROOT, 'app.manifest'),
)
