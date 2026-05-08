# Release process

HoLiLiHu ReClip dùng tag SemVer để phát hành.

## Versioning

- `MAJOR`: thay đổi phá vỡ API/CLI/MCP tool contract.
- `MINOR`: thêm tính năng tương thích ngược.
- `PATCH`: sửa lỗi hoặc cải thiện nhỏ.

Trong giai đoạn `0.x`, API có thể thay đổi nhanh hơn, nhưng release notes vẫn phải ghi rõ.

## Checklist

1. Cập nhật `CHANGELOG.md`.
2. Cập nhật version trong `pyproject.toml`.
3. Chạy kiểm thử:

   ```powershell
   .venv\Scripts\python.exe -m py_compile app.py downloader.py mcp_server.py reclip_holilihu_cli.py history.py settings.py desktop.py
   .venv\Scripts\python.exe tests\smoke_app.py
   .venv\Scripts\python.exe tests\smoke_mcp.py
   .venv\Scripts\reclip-holilihu-mcp.exe doctor
   ```

4. Commit:

   ```bash
   git commit -m "Release vX.Y.Z"
   ```

5. Tag:

   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

6. Kiểm tra GitHub Actions release workflow.
7. Kiểm tra GitHub Release có `HoLiLiHu-ReClip-Setup.exe`.

## After release

- Mở release page và kiểm asset tải được.
- Chạy smoke install trên máy sạch nếu có thể.
- Đóng/milestone các issue liên quan.
