# Ý tưởng
## Khái quát
### Nhận diện LED & Xử lý Quang học

* **Loại LED:** Linh kiện trong "image_9137de.png" là dạng **LED High Power (1W hoặc 3W)**. Loại này rất bền, độ sáng cao, phù hợp cho môi trường hoạt động thực tế.
* **Thấu kính (Optics):** Thay vì tự chế tạo thấu kính phức tạp, bạn nên mua **thấu kính TIR (Total Internal Reflection)** có góc chiếu hẹp (khoảng 15° - 30°) gắn vừa khít với bóng LED này. Để bẻ cong ánh sáng xuống đất, bạn có thể thiết kế và in 3D một chóa đèn (hood) có phần mui vát phía trên để cản tia sáng hắt lên trời và phản xạ chúng ngược xuống mặt đất cho camera Astra Pro.

### Linh kiện cho Smart Module

Để module tự tính toán thời gian chớp nháy và điều chỉnh độ sáng, bạn cần hai thành phần chính:

* **Vi điều khiển phụ (Sub-MCU):** Bạn nên dùng **CH32V003** hoặc **ATtiny85**. Chúng cực kỳ nhỏ gọn, giá thành rẻ, và có khả năng đọc tín hiệu lệnh (ví dụ: `1`, `2`, `11`...) để băm xung PWM mà không tốn diện tích mạch.
* **IC Nguồn dòng (LED Driver):** Tuyệt đối không dùng MOSFET đóng cắt trực tiếp vì LED High Power sẽ rất nhanh cháy do quá dòng. Hãy dùng IC **PT4115**. Đây là IC nguồn dòng không đổi (Constant Current) chuyên dụng, hiệu suất cao và có sẵn chân DIM để nhận trực tiếp tín hiệu PWM từ Sub-MCU.

### Tính toán & Mạch nguyên lý (Schematic)

* **Khối Logic:** Chân RX của Sub-MCU nối với mạch trung tâm (dùng chuẩn UART để gửi mã lệnh). Chân phát PWM của Sub-MCU nối vào chân DIM của PT4115.
* **Khối Công suất:** Quanh PT4115 sẽ cần cuộn cảm (thường 47uH - 68uH), Diode Schottky (VD: SS34) và tụ lọc nguồn (100uF).
* **Tính toán dòng điện:** Cường độ dòng qua LED được quyết định bởi điện trở xả $R_S$ nối với PT4115 theo công thức $I = \frac{0.1}{R_S}$. Ví dụ, nếu dùng LED 3W (dòng tiêu thụ ~700mA), bạn cần chọn $R_S \approx 0.15 \Omega$.

### Quy trình hoạt động của Module

* MCU trung tâm gửi 1 byte dữ liệu (Ví dụ: `0x0B` tương đương lệnh `11`).
* Sub-MCU nhận lệnh, kích hoạt Timer nội bộ để tự động phát xung PWM tắt/mở theo chu kỳ 1 giây.
* IC PT4115 cấp dòng điện nhấp nháy cho LED một cách mượt mà và ổn định.

Bạn dự định cho vi điều khiển trung tâm giao tiếp với các module đèn này qua chuẩn UART, I2C, hay chỉ dùng một chân Digital In đơn giản để đếm xung lệnh?
