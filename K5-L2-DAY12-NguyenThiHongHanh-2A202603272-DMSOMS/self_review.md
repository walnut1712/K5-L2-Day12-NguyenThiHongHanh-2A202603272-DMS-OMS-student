# Tự đánh giá — Nguyễn Thị Hồng Hạnh · G09

## 1. Tự rà soát 4 cảnh

Nghỉ tay 1 phút, mở lại bài của mình, chọn 4 ảnh (2 S##, 2 D##), đọc như người lạ.

Loại lỗi: `seat_flip`, `wrong_class`, `guess`, `box`, `missing`, `extra`, `lr_flip` (trái/phải mặt), `flag` (thiếu cờ điểm), `ok`.

| Ảnh | Đối tượng | Loại lỗi | Ghi chú | Đã sửa? |
|---|---|---|---|---|
| S01_rgb.png | infant_seat (rear_right) | ok | Hộp ôm sát nôi xách, vị trí ghế gọi theo xe chuẩn xác | Đã kiểm |
| S04_ir.png | infant_seat, child_seat | ok | Hai ghế trẻ em phân biệt rõ ràng, không bị lẫn lớp | Đã kiểm |
| D01.png | face, face13 | ok | Đủ 13 điểm keypoint, mắt kính clear nhìn rõ 2 mắt mở | Đã kiểm |
| D04.png | person, face | ok | Dây an toàn tuột lệch vai ghi đúng worn_incorrect, mắt bị che ghi unknown | Đã kiểm |

## 2. Lỗi mình lặp lại nhiều nhất hôm nay

Lỗi: Ban đầu dễ nhầm lẫn trục trái/phải khi quan sát camera OMS nhìn ngược chiều và camera DMS xoay góc 90°.

Vì sao mình mắc: Do thói quen nhìn theo thị giác khung hình thông thường thay vì chuyển sang hệ quy chiếu của người ngồi trên xe.

Lần sau tránh bằng cách: Luôn tự nhắc quy tắc: OMS trái ảnh là bên phải của xe; DMS ảnh xoay 90° thì mắt trái của tài xế nằm ở vị trí có tọa độ y lớn hơn.

## 3. Ghi chú về disagreement_log

Một dòng bạn của mình đúng và mình sai. Mình học được gì từ dòng đó:
Qua thảo luận với bạn Đặng Gia Tuấn ở dòng `S01_rgb.png` về thuộc tính `facing` của `infant_seat`, mình nhận thấy bạn đưa ra góc nhìn rất hợp lý từ tiêu chuẩn an toàn giao thông đường bộ (nôi sơ sinh luôn được thiết kế và quy định lắp đặt quay lưng về trước - rear-facing). Dù hai bên có cách tiếp cận khác nhau giữa trực quan camera và quy chuẩn xe hơi, việc đối chiếu giúp mình hiểu sâu hơn về bối cảnh thực tế của bài toán thị giác máy tính trong cabin ô tô.
