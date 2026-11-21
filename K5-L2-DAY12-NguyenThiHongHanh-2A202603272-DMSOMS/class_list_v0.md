# Danh sách lớp v0 — Nguyễn Thị Hồng Hạnh · G09

Viết tiếp từ slide 54 bài giảng. Mỗi lớp trả lời: **model cần nhận ra cái này để làm gì?**

## DMS (ít nhất 6 lớp)

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng DMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `face.eye_left` / `eye_right` | open / closed / unknown | Phát hiện dấu hiệu buồn ngủ (ngủ gật, nhắm mắt kéo dài / microsleep) | Có, trừ khi bị đốm lóa phản xạ LED hoặc kính râm tối |
| 2 | `face.gaze_zone` | road / mirror_l / mirror_r / mirror_c / cluster / center / lap / other | Phát hiện tài xế mất tập trung (nhìn điện thoại, nhìn màn hình quá lâu không quan sát đường) | Có, kết hợp hướng con ngươi và góc nghiêng đầu |
| 3 | `face.glasses` | unknown / none / clear / sun | Điều chỉnh thuật toán nhận diện mắt; phát hiện vật cản che khuất vùng mắt | Có, kính cận thấy gọng và tròng sáng, kính râm có thể trong suốt dưới NIR |
| 4 | `hand.on_wheel` | yes / no / unknown | Nhận diện tay trên vô lăng (Hands-On Detection) trong chế độ lái tự động L2/L3 | Có, phân biệt rõ bàn tay chạm vào vành vô lăng |
| 5 | `phone.state` | held / mounted / lap | Cảnh báo vi phạm hành vi sử dụng điện thoại khi đang điều khiển phương tiện | Có, nhận diện qua góc cạnh, viền và mặt phẳng thiết bị |
| 6 | `person.seatbelt` | worn_correct / worn_incorrect / not_worn / unknown | Cảnh báo tài xế chưa cài dây hoặc cài sai cách (vắt nách, sau lưng) để kích hoạt túi khí an toàn | Có, dải dây thường có độ tương phản độ sáng với áo |

## OMS (ít nhất 6 lớp)

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng OMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `infant_seat.facing` | rear / front | Tự động tắt túi khí ghế trước nếu lắp nôi ngược chiều; nhắc nhở chống bỏ quên trẻ (Child Presence Detection) | Có, nhận biết qua hình dạng nôi xách và tay xách |
| 2 | `child_seat.occupied` | no / unknown | Kiểm tra ghế an toàn trẻ em có đang được sử dụng hay để trống | Có, dựa vào hình khối ghế và người/vật bên trong |
| 3 | `person.seat` | rear_left / rear_middle / rear_right | Nhận diện sự hiện diện và vị trí người ngồi để tối ưu hóa điều hòa và kích hoạt túi khí tương ứng | Có, phân biệt rõ hình dạng cơ thể người |
| 4 | `person.seatbelt` | not_worn / unknown | Kiểm tra thắt dây an toàn hàng ghế sau để phát tín hiệu cảnh báo trên bảng điều khiển | Có (trên IR-sim chỉ gán not_worn hoặc unknown do đặc thù dataset) |
| 5 | `object.type` | bag / box / cup / other | Cảnh báo hành lý/vật dụng bỏ quên khi khóa xe; phát hiện vật thể có nguy cơ trượt gây nguy hiểm | Có, phân biệt qua hình học khối hộp, quai xách |
| 6 | `frame_meta.camera_blocked` | yes / no | Chẩn đoán lỗi phần cứng hoặc phát hiện camera cabin bị che khuất, bám bẩn | Có, nhận biết qua khung hình tối toàn phần hoặc mất nét hoàn toàn |

## 2 câu hỏi leo thang

Câu hỏi bạn muốn hỏi người viết guideline (hoặc khách hàng) vì guideline v1.0 chưa trả lời. Mỗi câu kèm **tên khung** làm ví dụ.

1. Câu hỏi: Thuộc tính `facing` của `infant_seat` được định nghĩa theo hệ quy chiếu hướng xe (rear-facing là quay mặt em bé về đuôi xe) hay hướng quan sát của camera cabin (front là mặt nôi quay về phía camera)?
   Khung ví dụ: `S01_rgb.png` (ghế `rear_right`).
   Bạn tạm gán thế nào và vì sao: Tạm gán `front` theo góc nhìn trực quan thấy lòng nôi hướng về phía trước của khung hình camera, nhưng đề xuất chuẩn hóa theo quy chuẩn an toàn xe hơi quốc tế (`rear-facing` tức là `rear` theo trục xe).

2. Câu hỏi: Trên ảnh DMS tài xế, khi tài xế cầm chai nước, cốc uống hoặc vật thể khác không phải điện thoại trên tay thì có cần vẽ box `object` hay không?
   Khung ví dụ: `D05.png` (tài xế thao tác cầm đồ vật).
   Bạn tạm gán thế nào và vì sao: Tạm gán chỉ vẽ `hand` và không vẽ `object`, vì theo Guideline §4.2 phần Không gán của DMS ghi rõ "chai, cốc, kính và vật khác trên tay: DMS không vẽ object, cũng không ghi là phone" nhằm tối ưu cho bài toán tập trung vào tài xế.
