# Localization

HoLiLiHu ReClip hiện chỉ ưu tiên tiếng Việt.

## Current language status

- Web UI: tiếng Việt.
- Desktop title/text: tiếng Việt.
- User-facing errors: phần lớn tiếng Việt.
- Community docs: tiếng Việt là chính.
- README hiện có một số đoạn tiếng Anh để dễ đọc trên GitHub quốc tế, nhưng trạng thái sản phẩm vẫn là Vietnamese-first.

## Future multilingual work

Trước khi thêm tiếng Anh hoặc ngôn ngữ khác, nên:

1. Tách chuỗi UI ra khỏi `templates/index.html`.
2. Tạo file locale, ví dụ `locales/vi.json` và `locales/en.json`.
3. Thêm setting chọn ngôn ngữ.
4. Thêm test để không thiếu key dịch.

## Contribution rule

Trong giai đoạn hiện tại, chuỗi UI mới nên viết bằng tiếng Việt. Nếu contributor muốn thêm tiếng Anh, hãy mở issue thiết kế localization trước.
