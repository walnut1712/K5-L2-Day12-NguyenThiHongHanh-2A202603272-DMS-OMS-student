# Khai báo dùng AI — Nguyễn Thị Hồng Hạnh

Không dùng AI thì xóa bảng và ghi: **Không dùng.**

Nhắc lại: không đưa ảnh cabin hay ảnh tài xế (kể cả ảnh chụp màn hình) cho bất kỳ công cụ AI nào.

| # | Công cụ | Bạn hỏi gì (tóm tắt) | Bạn dùng kết quả thế nào | Bạn có kiểm lại không? Bằng gì? |
|---|---|---|---|---|
| 1 | Antigravity AI Assistant | Hỗ trợ đối chiếu các điểm khác biệt giữa 2 file export CVAT (disagreement_log) với các điều khoản của Guideline Cabin v1.0 | Điền các cột verdict, guideline_rule và action trong file disagreement_log.csv | Có, tự tra cứu đối chiếu lại trực tiếp với GUIDE.md và RULES.md |
| 2 | Antigravity AI Assistant | Giải thích nguyên lý vật lý của bước sóng NIR 940nm và kiểm tra công thức tính thời gian gián đoạn nhìn đường theo frame/fps | Trả lời và kiểm tra các câu hỏi trong exit_ticket.md | Có, tự tính lại: (314 - 240 + 1) / 30 = 2.50 giây |
| 3 | Antigravity AI Assistant | Hướng dẫn kiểm tra định dạng và cấu trúc gói nộp bài theo chuẩn SUBMISSION.md | Kiểm tra tính hợp lệ của file export và danh mục tệp nộp bài | Có, chạy lệnh cabin_check.py và zipfile inspection qua terminal |
