# TEAM — Ngày 12

Mã bộ ảnh: **G09** · Hình thức: cá nhân

| Họ tên | MSSV | Đã gán đủ 22 ảnh? | Review chéo với (peer diff) | Số dòng disagreement đã xử lý |
|---|---|---|---|---|
| Nguyễn Thị Hồng Hạnh | 2A202603272 | có | Đặng Gia Tuấn | 30 |

Ca hai bạn vẫn không thống nhất và đã hỏi coach (ghi tên ảnh + đối tượng):

- `S01_rgb.png` / `S01_ir.png` (`infant_seat`): Thống nhất quy ước giá trị `facing` của nôi trẻ em sơ sinh (theo hướng xe hay hướng camera).
- `D01.png` - `D06.png` (`frame_meta.light`): Quy ước giá trị `light` trên ảnh hồng ngoại NIR đơn sắc khi không quan sát được điều kiện ngoài trời (`unknown` theo nguyên tắc không đoán vs `night`).

## Cá nhân

Mỗi người một mục, 1–2 dòng mỗi ý.

### NguyenThiHongHanh-2A202603272
- Phần mình làm: Tự gán đủ 22 ảnh cốt lõi, chạy tự kiểm tra cabin_check qua các checkpoint A, B, Final đạt 0 lỗi 0 cảnh báo; chạy so sánh diff với bạn Đặng Gia Tuấn và rà soát xử lý toàn bộ 30 điểm khác biệt theo Guideline Cabin v1.0.
- Điều mình học được hôm nay: Hiểu rõ đặc tính quang học của cảm biến NIR 940nm trong cabin, sự khác biệt giữa IR thật và IR giả lập, và tầm quan trọng của việc tuân thủ quy tắc không đoán (unknown) đối với các trường hợp bị che khuất hoặc thiếu thông tin.
