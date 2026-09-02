# 🚀 Báo Cáo Tiến Độ Dự Án BPURD - Phân Hệ Thị Giác (Vision Hub)
**Ngày thực hiện:** 02/09/2026
**Mục tiêu:** Xây dựng hệ sinh thái nhận thức không gian cho Robot Dog sử dụng Raspberry Pi 4 và camera 3D Orbbec Astra Pro.

---

## 🏗️ 1. Môi Trường & Kiến Trúc Hệ Thống
*   **Dockerization:** Đóng gói thành công toàn bộ Driver ROS 2 Humble và các module AI vào chung một container (`astra_pro_humble`). Đảm bảo nguyên tắc "Write once, run anywhere", sẵn sàng triển khai chéo lên các board mạch ARM64 khác.
*   **Xử lý Xung đột Phần cứng:** Tối ưu hóa băng thông USB trên Host OS (`usbfs_memory_mb = 1000`) và bypass driver `uvcvideo` để tránh nghẽn cổ chai dữ liệu 3D.
*   **Dependency Locking:** Giải quyết triệt để lỗi `cv_bridge` (Segmentation fault) bằng cách khóa cứng phiên bản `numpy<2.0.0`, đồng thời tích hợp `Flask==3.1.3` và `mediapipe==0.10.14` trực tiếp vào quá trình build Docker.

---

## 🧠 2. Các Module AI Đã Phát Triển (OOP Architecture)

Toàn bộ các tính năng được thiết kế theo chuẩn ROS 2 Node lỏng (Decoupled Architecture), giao tiếp qua Topic, giúp Pi 4 không bị quá tải.

### 2.1. Web Streamer (`web_streamer.py`)
*   **Chức năng:** Trạm phát sóng trung tâm. Chạy độc lập trên một luồng (Thread) sử dụng Flask.
*   **Đầu vào:** Subscribe vào các Topic hình ảnh đã qua xử lý của AI (ví dụ: `/bpurd/vision/gesture_image`).
*   **Đầu ra:** Giao diện Web MJPEG Stream tại `http://<IP>:5000/video_feed` phục vụ giám sát và debug từ xa.

### 2.2. Trạm Cảnh Báo Va Chạm 3D (`obstacle_monitor.py`)
*   **Chức năng:** Phân tích bản đồ chiều sâu (Depth Map).
*   **Cơ chế:** Lấy ROI trung tâm từ `/camera/depth/image_raw`, tính toán khoảng cách mét thực tế. Phát tín hiệu `DANGER` (Cảnh báo) hoặc số liệu khoảng cách để né vật cản tĩnh.

### 2.3. Điều Khiển Bằng Cử Chỉ (`gesture_controller.py` & `gesture_library.py`)
*   **Kiến trúc:** Tách bạch Single Responsibility. `gesture_library.py` (Chứa não bộ MediaPipe và thư viện toán học từ điển tay) - `gesture_controller.py` (Chứa ROS 2 Node).
*   **Cơ chế:** Nhận diện điểm ảnh bàn tay (Landmarks), phân tích logic để ra lệnh `STOP` hoặc `FORWARD`. In HUD Overlay Text (Đỏ/Xanh) trực tiếp lên luồng ảnh gửi về Web Streamer. Bắn lệnh ra topic `/bpurd/control/gesture_cmd`.

### 2.4. Trạm Xuất Mây Điểm 3D (`pointcloud_exporter.py`)
*   **Chức năng:** "Chụp ảnh" không gian 3D.
*   **Cơ chế:** Bóc tách dữ liệu từ `/camera/depth/points`. Tự động tính toán thuật toán Lidar Heatmap (Đỏ -> Xanh dương) dựa trên trục Z (khoảng cách) bằng thư viện `colorsys`.
*   **Đầu ra:** Xuất file chuẩn công nghiệp `.ply` có thể mở mượt mà trên MeshLab hoặc Web 3D.

### 2.5. Hệ Thống "Follow Me" (`target_tracker.py`)
*   **Chức năng:** Khóa và bám đuổi mục tiêu động.
*   **Cơ chế (Sensor Fusion nhẹ):** Dùng OpenCV lọc màu HSV trên ảnh Color để tìm tọa độ (X, Y) của vật thể. Áp tọa độ đó sang ảnh Depth để lấy khoảng cách thực tế (Z).
*   **Đầu ra:** Tính toán PID cơ bản để xuất lệnh di chuyển tiến/lùi, xoay trái/phải ra topic `/cmd_vel` cho động cơ.

---

## ⚙️ 3. Bài Học & Chiến Thuật Quản Lý Tài Nguyên
*   **Không chạy đồng thời 100% công suất:** Rút kinh nghiệm từ giới hạn phần cứng của Pi 4, thay vì dùng một file `launch` ép tất cả AI chạy cùng lúc, hệ thống sẽ sử dụng **Máy trạng thái (State Machine)** hoặc **ROS 2 Lifecycle Nodes**.
*   **Thực thi ngữ cảnh:** Chỉ đánh thức module (ví dụ: MediaPipe) khi có tín hiệu kích hoạt (như phát hiện người), các thời gian khác duy trì trạng thái ngủ đông (return ngay tại hàm callback) để giải phóng CPU cho Navigation.

---
*Tài liệu này được tạo tự động nhằm lưu trữ tiến trình phát triển kiến trúc điều khiển tự hành cho dự án Robot Dog.*