"""Tao bo cai HoLiLiHu ReClip - 1 file setup.exe."""
import os
import sys
import io
import zipfile
import subprocess

# Fix encoding cho Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJ_DIR, 'dist')
OUTPUT = os.path.join(PROJ_DIR, 'HoLiLiHu-ReClip-Setup.exe')
STUB_SCRIPT = os.path.join(PROJ_DIR, 'installer_stub.py')
ICO = os.path.join(PROJ_DIR, 'assets', 'app.ico')


def create_installer():
    print("=== Tạo bộ cài HoLiLiHu ReClip ===\n")

    # 1. Build installer stub exe
    print("[1/3] Build installer stub...")
    import tempfile
    tmp = tempfile.mkdtemp()
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--onefile', '--console',
        '--name', 'HoLiLiHu-ReClip-Setup',
        '--distpath', os.path.dirname(OUTPUT),
        '--workpath', os.path.join(tmp, 'build'),
        '--specpath', tmp,
        '--clean', '--noconfirm',
        '--icon', ICO,
        STUB_SCRIPT,
    ], capture_output=True, text=True, timeout=180)

    if result.returncode != 0:
        print("Lỗi build stub:")
        print(result.stderr[-800:])
        return

    if not os.path.isfile(OUTPUT):
        print("Không tìm thấy stub exe!")
        return

    print(f"  Stub: {os.path.getsize(OUTPUT) // (1024*1024)} MB")

    # 2. Nén dist/ thành zip
    print("\n[2/3] Đóng gói ứng dụng...")
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for fname in os.listdir(DIST_DIR):
            fpath = os.path.join(DIST_DIR, fname)
            if os.path.isfile(fpath):
                size_mb = os.path.getsize(fpath) // (1024 * 1024)
                print(f"  + {fname} ({size_mb} MB)")
                zf.write(fpath, fname)

    zip_data = zip_buf.getvalue()
    print(f"  Zip: {len(zip_data) // (1024*1024)} MB")

    # 3. Nối zip vào cuối exe
    print("\n[3/3] Ghép vào installer...")
    with open(OUTPUT, 'ab') as f:
        f.write(zip_data)

    final_mb = os.path.getsize(OUTPUT) // (1024 * 1024)
    print(f"\n{'=' * 50}")
    print(f"  HOÀN TẤT: {OUTPUT}")
    print(f"  Kích thước: {final_mb} MB")
    print(f"{'=' * 50}")


if __name__ == '__main__':
    create_installer()
