# 🚀 Hướng Dẫn Khởi Động & Kiểm Thử Thị Giác Astra Pro (BPURD)

Quy trình này hướng dẫn cách khởi động phần cứng camera Astra Pro qua Docker và chạy các module nhận thức không gian (Vision Apps) cho Robot Dog.

---

## 🛠️ Giai Đoạn 1: Đánh Thức Camera (Chạy Docker)

Thực hiện các bước này mỗi khi bật mạch hoặc cắm lại cáp USB để cấp quyền phần cứng và bật luồng ROS 2.

**1. Giải phóng băng thông & Tắt Driver Host**
Mở terminal và chạy lệnh dọn đường:
```bash
# Mở rộng bộ nhớ đệm USB lên 1000MB để chống rớt gói tin 3D
sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'

# Tạm tắt driver UVC của Host để nhường toàn quyền cho Docker
sudo rmmod uvcvideo
```

**2. Khởi động hệ sinh thái Docker**
Di chuyển vào workspace và gọi Compose:

```bash
cd ~/beniot_dev/BPURD-BeniotPhanUltimateRobotDog/pi4-ws/camera-astra-pro-ws
docker compose up -d

```

**3. Nghiệm thu phần cứng**
Kiểm tra log để đảm bảo camera đã "mở mắt" (Bấm `Ctrl+C` để thoát xem log):

```bash
docker logs -f astra_pro_humble

```

---

## 🧠 Giai Đoạn 2: Chạy Ứng Dụng Thị Giác (Vision Apps)

Sau khi Docker đã chạy ngầm và phát dữ liệu, chúng ta sẽ bật các module phân tích AI/Logic.

**Chạy Tính Năng 1: Cảnh Báo Va Chạm (Obstacle Monitor)**
Mở một terminal mới và chạy script Python:

```bash
export ROS_DOMAIN_ID=30
python3 obstacle_monitor.py

```

*(Giữ terminal này mở để script liên tục xử lý dữ liệu chiều sâu).*

---

## 📡 Giai Đoạn 3: Lắng Nghe & Nghiệm Thu (ROS 2 Topics)

Mở thêm một **Terminal hoàn toàn mới** để đóng vai trò là "Hệ thống di chuyển của Robot" đang lắng nghe cảnh báo từ camera.

**1. Đồng bộ mạng ROS 2:**

```bash
export ROS_DOMAIN_ID=30

```

**2. Xem cảnh báo nguy hiểm bằng chữ:**
Đưa tay ra trước camera để thấy dữ liệu nhảy liên tục:

```bash
ros2 topic echo /bpurd/vision/obstacle_alert

```

**3. Xem khoảng cách thực tế (theo mét):**

```bash
ros2 topic echo /bpurd/vision/front_distance

```

```


