# Security Policy

## Supported versions

Dự án đang ở giai đoạn `0.x`. Chỉ nhánh `main` và bản release mới nhất được ưu tiên xử lý bảo mật.

## Reporting a vulnerability

Không đăng công khai cookies, token, file cấu hình riêng tư, hoặc link khai thác chi tiết trong issue công khai.

Nếu GitHub Security Advisories/private vulnerability reporting được bật cho repo, hãy dùng kênh đó. Nếu chưa bật, mở issue với tiêu đề chung chung như `Security report request` và không kèm chi tiết nhạy cảm; maintainer sẽ chuyển sang kênh riêng.

Vui lòng cung cấp:

- Phiên bản hoặc commit đang dùng.
- Hệ điều hành và cách chạy: web app, desktop installer, CLI, hay MCP.
- Mô tả tác động bảo mật.
- Các bước tái hiện tối thiểu, đã lược bỏ bí mật.

## Scope

Trong phạm vi:

- Rò rỉ cookies, token, đường dẫn file nhạy cảm.
- Command execution ngoài ý muốn qua CLI/MCP.
- Lỗi tải file gây ghi đè ngoài thư mục cấu hình.
- Lỗi cấu hình MCP làm chạy command không mong muốn.

Ngoài phạm vi:

- Việc nền tảng nguồn chặn tải video theo điều khoản riêng.
- Yêu cầu né tránh DRM, paywall, giới hạn truy cập, hoặc bản quyền.
- Vấn đề trong dependency upstream nếu chưa có tác động cụ thể đến HoLiLiHu ReClip.
