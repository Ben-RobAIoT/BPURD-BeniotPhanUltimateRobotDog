### 1. Chuẩn bị Phần cứng

Bạn có 2 lựa chọn phổ biến nhất cho người mới bắt đầu:

1. **STM32 Nucleo Board (Khuyên dùng):** Mạch của STMicroelectronics, đã tích hợp sẵn mạch nạp và gỡ lỗi (ST-Link) trên board. Cắm cáp USB vào máy tính là dùng được ngay.
2. **STM32 Blue Pill (STM32F103C8T6) + ST-Link V2:** Lựa chọn cực kỳ rẻ và phổ biến. Bạn sẽ cần mua thêm một USB ST-Link V2 để nạp code từ máy tính vào mạch.

---

### 2. Thiết lập môi trường & Chạy thử "Hello World" (Nháy LED)

Công cụ chuẩn nhất hiện nay là **STM32CubeIDE** (hoàn toàn miễn phí từ ST), nó tích hợp sẵn phần mềm cấu hình đồ họa (CubeMX) và trình biên dịch C/C++. Quá trình quản lý phiên bản code bằng Git/GitHub trên IDE này cũng tương tự như các dự án thông thường.

1. **Cài đặt STM32CubeIDE:**
Tải và cài đặt phần mềm STM32CubeIDE từ trang chủ STMicroelectronics. Bạn sẽ cần tạo một tài khoản ST miễn phí để tải.


2. **Tạo dự án mới:**
Mở IDE, chọn `File -> New -> STM32 Project`. Nhập mã vi điều khiển của bạn (ví dụ: `STM32F103C8` cho Blue Pill) và đặt tên dự án.


3. **Cấu hình chân GPIO qua giao diện đồ họa:**
Giao diện file `.ioc` sẽ hiện lên (đây là CubeMX tích hợp).
Trên hình vẽ con chip, click vào chân nối với LED (ví dụ chân `PC13` trên mạch Blue Pill) và chọn **GPIO_Output**. Nhấn `Ctrl + S` để IDE tự động sinh code C.


4. **Viết code điều khiển:**
Mở file `main.c` trong thư mục `Core/Src`. Tìm đến vòng lặp `while (1)` và thêm dòng code sau để đảo trạng thái LED và tạo độ trễ:

```c
HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
HAL_Delay(1000); // Trễ 1000ms (1 giây)

```


5. **Biên dịch và Nạp code (Debug):**
Nhấn nút hình con bọ (Debug) trên thanh công cụ. IDE sẽ tự động biên dịch, nạp code qua ST-Link vào chip. Mạch của bạn sẽ bắt đầu nhấp nháy đèn LED.


---

### 3. Lộ trình học sâu về kiến trúc ARM và Ứng dụng

Khi đã chạy được bài cơ bản, để hiểu sâu về cách ARM Cortex-M hoạt động và áp dụng vào các dự án thực tế, bạn nên đi theo thứ tự sau:

**Giai đoạn 1: Làm chủ ngoại vi cơ bản (Peripherals)**
Đừng dùng thư viện HAL (Hardware Abstraction Layer) một cách máy móc. Hãy đọc Reference Manual của chip để hiểu cấu trúc thanh ghi.

* **GPIO:** Cách cấu hình input/output, pull-up/pull-down.
* **UART/USART:** Giao tiếp nối tiếp. Bắt buộc phải nắm rõ để in log ra terminal máy tính hoặc giao tiếp với module GPS.
* **Timer & PWM:** Dùng Timer để tạo độ trễ chính xác. Dùng PWM để điều khiển tốc độ động cơ không chổi than (ESC).
* **ADC:** Chuyển đổi tín hiệu tương tự sang số (ví dụ: đọc giá trị điện áp pin hoặc cảm biến analog).
* **I2C / SPI:** Giao tiếp tốc độ cao với các cảm biến (như IMU MPU6050 để đo góc nghiêng, cực kỳ quan trọng trong điều khiển bay).

**Giai đoạn 2: Sức mạnh cốt lõi của kiến trúc ARM**
Đây là lúc bạn phân biệt được người mới học và kỹ sư nhúng:

* **Ngắt (Interrupts) & NVIC:** Thay vì liên tục kiểm tra xem có dữ liệu đến không (polling), hãy cấu hình ngắt để CPU tự phản hồi ngay lập tức khi có sự kiện (ví dụ: có tín hiệu từ tay cầm điều khiển RC). ARM Cortex-M có bộ điều khiển ngắt lồng nhau (NVIC) rất mạnh mẽ.
* **DMA (Direct Memory Access):** Cho phép dữ liệu chuyển thẳng từ ngoại vi (như cảm biến) vào bộ nhớ RAM mà không cần CPU can thiệp. Giúp CPU rảnh tay tính toán các thuật toán phức tạp như PID.

**Giai đoạn 3: Hệ điều hành thời gian thực (RTOS)**
Khi hệ thống lớn lên (ví dụ một trạm quan trắc đô thị đa chức năng), việc gom tất cả vào một vòng lặp `while (1)` sẽ gây tắc nghẽn.
