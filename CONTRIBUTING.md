# Contributing

Cảm ơn bạn muốn đóng góp cho HoLiLiHu ReClip. Dự án hiện đang ở giai đoạn đầu, ưu tiên tiếng Việt cho giao diện, tài liệu vận hành, và trao đổi issue. Pull request bằng tiếng Anh vẫn được chấp nhận nếu nội dung rõ ràng.

## Nguyên tắc chung

- Tôn trọng giấy phép MIT và attribution của ReClip gốc.
- Không thêm tính năng tải nội dung theo hướng né tránh bảo vệ bản quyền hoặc vi phạm điều khoản nền tảng.
- Ưu tiên thay đổi nhỏ, dễ review, có kiểm thử hoặc mô tả cách kiểm chứng.
- Không commit `.venv/`, `build/`, `dist/`, installer, file tải xuống, cookies, hoặc dữ liệu cá nhân.
- Giữ UI hiện tại bằng tiếng Việt. Nếu thêm chuỗi hiển thị mới, dùng tiếng Việt nhất quán.

## Thiết lập môi trường

```powershell
py -3.10 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
```

Chạy web app:

```powershell
.venv\Scripts\python.exe app.py
```

Chạy MCP server:

```powershell
.venv\Scripts\python.exe -m mcp_server
```

## Kiểm thử trước khi mở PR

```powershell
.venv\Scripts\python.exe -m py_compile app.py downloader.py mcp_server.py reclip_holilihu_cli.py history.py settings.py desktop.py
.venv\Scripts\python.exe tests\smoke_app.py
.venv\Scripts\python.exe tests\smoke_mcp.py
.venv\Scripts\reclip-holilihu.exe print-mcp-config codex --source .
.venv\Scripts\reclip-holilihu.exe doctor
```

## Quy trình pull request

1. Mở issue trước nếu thay đổi lớn hoặc thay đổi hành vi người dùng.
2. Tạo branch ngắn gọn, ví dụ `feature/mcp-status` hoặc `fix/download-queue`.
3. Mô tả rõ vấn đề, cách sửa, và cách kiểm thử trong PR.
4. Cập nhật `CHANGELOG.md` nếu thay đổi ảnh hưởng người dùng.
5. Cập nhật `README.md` hoặc docs nếu thêm lệnh, setting, hoặc flow mới.

## Phiên bản và release

Dự án dùng SemVer:

- `MAJOR`: thay đổi phá vỡ API/CLI/MCP tool contract.
- `MINOR`: thêm tính năng tương thích ngược.
- `PATCH`: sửa lỗi hoặc cải thiện nhỏ.

Vì dự án đang ở `0.x`, API có thể còn thay đổi trong quá trình ổn định.
