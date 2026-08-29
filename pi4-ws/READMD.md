
# Tài liệu Hướng dẫn sử dụng (Documentation)

Một kỹ sư robot giỏi không chỉ viết code xịn mà còn phải viết "hướng dẫn sử dụng" xịn. Cậu hãy tạo một file tên là `README.md` đặt ngay bên trong thư mục `pi4-ws/camera-astra-pro-ws/` và dán nguyên văn bản Markdown tuyệt đẹp này vào nhé:

```markdown
# 📷 Orbbec Astra Pro - Edge Computing Setup for BPURD

Module này chứa toàn bộ cấu trúc Docker siêu nhẹ (dựa trên ROS 2 Humble) để vận hành camera 3D Orbbec Astra Pro trên Raspberry Pi 4 (8GB). Hệ thống đã được tinh chỉnh để giải quyết triệt để các vấn đề nghẽn cổ chai USB và xung đột Driver UVC trên Linux.

## ⚙️ Yêu cầu phần cứng
*   **Board mạch:** Raspberry Pi 4 Model B (Khuyến nghị bản 8GB RAM).
*   **Camera:** Orbbec Astra Pro.
*   **Kết nối:** Cắm trực tiếp camera vào cổng **USB 3.0 (Xanh dương)** của Pi 4. Tránh cắm qua USB Hub không có nguồn phụ để chống sụt áp (`statusCode: 1004`).

## 🚀 Hướng dẫn cài đặt & Khởi động (Chỉ tốn 1 phút)

### 1. Giải phóng băng thông USB (Bắt buộc trên Pi 4)
Mặc định Pi 4 chỉ cấp 16MB RAM cho cổng USB, không đủ để truyền ảnh 3D. Cần mở rộng lên 1000MB:
```bash
sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'

```

### 2. Tránh xung đột Driver Camera (Bắt buộc)

Hệ điều hành Host thường tự động giành quyền điều khiển camera màu. Cần vô hiệu hóa driver mặc định để nhường toàn quyền cho Docker:

```bash
sudo rmmod uvcvideo

```

### 3. Build và Khởi chạy Docker

Hệ thống sẽ tự động tải mã nguồn `ros2_astra_camera`, cài đặt thư viện (`libglog`, `libuvc`...) và tự động kích hoạt luồng ROS 2.

```bash
cd pi4-ws/camera-astra-pro-ws
docker compose up -d --build

```

## 🔍 Nghiệm thu & Kiểm tra

Xem log trực tiếp để đảm bảo camera đã "mở mắt":

```bash
docker logs -f astra_pro_humble

```

*(Thành công khi log hiển thị dòng: `device started.`)*

Liệt kê các Topic hình ảnh (Depth, IR, Color) đang được phát xuyên qua Host:

```bash
ros2 topic list

```

## 🛠️ Xử lý sự cố thường gặp (Troubleshooting)

* **Lỗi `statusCode: 8` hoặc `sequence size exceeds remaining buffer`:** Thường do thiếu nguồn điện hoặc quên chạy lệnh mở rộng RAM USB (Bước 1). Hãy rút các thiết bị USB khác ra để thử lại.
* **Treo terminal khi gõ lệnh launch:** Do quên chạy Bước 2, Host và Docker đang giành giật quyền truy cập `/dev/video`.

```

Chỉ cần làm theo đúng 3 bước này, repo GitHub của cậu sẽ cực kỳ ngăn nắp, đầy đủ thông tin, và quan trọng nhất là "bất tử". Cậu cứ yên tâm đẩy code lên nhé, tôi đã nằm sẵn sàng trong file `docker-compose.yml` để chờ ngày kết hợp Sensor Fusion cùng cậu rồi!

```