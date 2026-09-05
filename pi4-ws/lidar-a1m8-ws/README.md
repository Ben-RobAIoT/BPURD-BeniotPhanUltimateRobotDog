## Hướng dẫn Thiết lập và Vận hành RPLiDAR A1M8 trên ROS 2

Tài liệu này quy định các bước cấu hình phần cứng, cấp quyền giao tiếp tĩnh và biên dịch mã nguồn để vận hành cảm biến không gian RPLiDAR A1M8.

---

### 1. Nhận diện Phần cứng và Cấp quyền Giao tiếp tĩnh

Hệ điều hành Linux mặc định quản lý thiết bị ngoại vi qua cổng USB một cách ngẫu nhiên. Việc thiết lập quy tắc `udev` giúp hệ thống luôn gán một định danh cố định cho LiDAR, đảm bảo tính ổn định khi chạy thuật toán tự hành.

**Xác định cổng kết nối thiết bị:**
Sử dụng các lệnh sau để tìm vị trí cổng USB mà LiDAR đang kết nối.

```bash
lsusb
ls -l /dev/ttyUSB*

```

**Thiết lập quy tắc udev vĩnh viễn:**
Mở trình soạn thảo hệ thống để tạo file quy tắc mới.

```bash
sudo nano /etc/udev/rules.d/rplidar.rules

```

Dán cấu hình nhận diện phần cứng bên dưới vào file:

```text
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE:="0666", GROUP:="dialout", SYMLINK+="rplidar"

```

**Ý nghĩa các tham số cấu hình:**

* `ATTRS{idVendor}=="10c4"` và `ATTRS{idProduct}=="ea60"`: Mã định danh phần cứng, giúp hệ thống nhận diện chính xác mạch CP210x của LiDAR.
* `MODE:="0666"`: Cấp quyền đọc/ghi dữ liệu vĩnh viễn cho tất cả người dùng.
* `SYMLINK+="rplidar"`: Tạo đường dẫn ảo tĩnh. Mã nguồn từ nay chỉ cần gọi cổng `/dev/rplidar` thay vì `ttyUSBx`.

**Áp dụng và kiểm tra quy tắc:**
Kiểm tra lại nội dung file và nạp lại cấu hình vào lõi hệ điều hành.

```bash
cat /etc/udev/rules.d/rplidar.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -l /dev/rplidar

```

---

### 2. Tải Mã nguồn và Biên dịch (Workspace Setup)

Mã nguồn ROS 2 bắt buộc phải được đặt trong thư mục `src` của không gian làm việc (workspace).

**Khởi tạo thư mục và tải thư viện:**

```bash
mkdir -p src
cd src
git clone https://github.com/Slamtec/sllidar_ros2.git

```

**Biên dịch không gian làm việc:**
Trở lại thư mục gốc của workspace, nạp môi trường ROS 2 và tiến hành biên dịch gói sllidar.

```bash
cd ..
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install

```

---

### 3. Khởi chạy Node và Kiểm thử Dữ liệu

Sau khi biên dịch thành công, hệ thống cần được nạp các file thực thi để có thể giao tiếp với phần cứng.

**Kiểm tra kịch bản khởi chạy (Launch files):**
Dòng LiDAR A1M8 sẽ có file khởi chạy riêng biệt. Lệnh dưới đây giúp xác nhận tên file chính xác do nhà sản xuất cung cấp.

```bash
ls src/sllidar_ros2/launch

```

**Kích hoạt cảm biến:**
Nạp lại môi trường không gian làm việc sau khi biên dịch và gọi file launch tương ứng, đồng thời truyền tham số cổng tĩnh đã cấu hình ở bước 1.

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch sllidar_ros2 sllidar_a1_launch.py serial_port:=/dev/rplidar

```

**Kiểm thử luồng dữ liệu:**
Mở một cửa sổ Terminal mới để giám sát dữ liệu thô dạng số (mảng khoảng cách và cường độ quét) do LiDAR phát ra trên Topic mạng.

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /scan

```

