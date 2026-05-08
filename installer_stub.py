"""HoLiLiHu ReClip - Bo cai dat."""
import os
import sys
import io
import struct
import zipfile
import shutil
import subprocess

APP_NAME = "HoLiLiHu ReClip"
EXE_NAME = "HoLiLiHu-ReClip.exe"


def main():
    print()
    print("=" * 50)
    print("  Cai dat " + APP_NAME)
    print("=" * 50)
    print()

    install_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        APP_NAME,
    )
    print("  Thu muc cai dat: " + install_dir)
    print()

    # Giai nen tu cuoi file exe
    print("  [1/3] Dang giai nen...")
    exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    with open(exe_path, 'rb') as f:
        data = f.read()

    # Tim zip data (PK header)
    zip_start = -1
    eocd = data.rfind(b'PK\x05\x06')
    if eocd != -1:
        cd_offset = struct.unpack('<I', data[eocd + 16:eocd + 20])[0]
        zip_start = data.rfind(b'PK\x03\x04', 0, cd_offset + 1)

    if zip_start == -1:
        zip_start = data.find(b'PK\x03\x04')

    if zip_start == -1:
        print("  LOI: Khong tim thay du lieu cai dat!")
        input("  Nhan Enter de dong...")
        return

    zip_data = data[zip_start:]
    os.makedirs(install_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zf.extractall(install_dir)
    except Exception as e:
        print("  LOI giai nen: " + str(e))
        input("  Nhan Enter de dong...")
        return

    print("  Da giai nen vao: " + install_dir)

    # Tao shortcut Desktop
    print("  [2/3] Tao shortcut tren Desktop...")
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, APP_NAME + ".lnk")
        target = os.path.join(install_dir, EXE_NAME)

        ps_script = (
            '$ws = New-Object -ComObject WScript.Shell; '
            '$s = $ws.CreateShortcut("' + shortcut_path.replace('\\', '\\\\') + '"); '
            '$s.TargetPath = "' + target.replace('\\', '\\\\') + '"; '
            '$s.WorkingDirectory = "' + install_dir.replace('\\', '\\\\') + '"; '
            '$s.Description = "' + APP_NAME + ' - Tai video mien phi"; '
            '$s.Save()'
        )
        subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, timeout=10,
        )
        print("  Shortcut Desktop: OK")
    except Exception as e:
        print("  Khong tao duoc shortcut: " + str(e))

    # Tao shortcut Start Menu
    print("  [3/3] Tao shortcut Start Menu...")
    try:
        start_menu = os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft", "Windows", "Start Menu", "Programs",
        )
        sm_path = os.path.join(start_menu, APP_NAME + ".lnk")
        target = os.path.join(install_dir, EXE_NAME)
        ps_script = (
            '$ws = New-Object -ComObject WScript.Shell; '
            '$s = $ws.CreateShortcut("' + sm_path.replace('\\', '\\\\') + '"); '
            '$s.TargetPath = "' + target.replace('\\', '\\\\') + '"; '
            '$s.WorkingDirectory = "' + install_dir.replace('\\', '\\\\') + '"; '
            '$s.Save()'
        )
        subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, timeout=10,
        )
        print("  Shortcut Start Menu: OK")
    except Exception:
        pass

    print()
    print("  " + "=" * 46)
    print("  Cai dat thanh cong!")
    print("  Thu muc: " + install_dir)
    print("  " + "=" * 46)
    print()

    answer = input("  Mo ung dung ngay? (Y/n): ").strip().lower()
    if answer != 'n':
        app_exe = os.path.join(install_dir, EXE_NAME)
        subprocess.Popen([app_exe], cwd=install_dir)
        print("  Dang mo ung dung...")

    print()
    print("  Cam on ban da cai dat! Nhan Enter de dong.")
    input()


if __name__ == "__main__":
    main()
