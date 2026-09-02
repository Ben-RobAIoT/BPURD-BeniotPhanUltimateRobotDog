### 🚀 Quy trình Khởi động Camera Astra Pro (Daily Startup Guide)

Quy trình này cần thực hiện mỗi khi Raspberry Pi 4 vừa được bật lên hoặc khởi động lại. Cấp quyền phần cứng trước, gọi Docker sau.

**Bước 1: Giải phóng băng thông USB & Tắt Driver Host**
Mở một terminal mới trên hệ điều hành Host (Jazzy) và chạy hai lệnh sau để dọn đường cho camera:

```bash
# Mở rộng bộ nhớ đệm USB lên 1000MB để không bị rớt gói tin 3D
sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'

# Tạm tắt driver UVC của Host để nhường toàn quyền điều khiển cho Docker
sudo rmmod uvcvideo

```

**Bước 2: Kích hoạt Hệ sinh thái Docker**
Di chuyển vào đúng thư mục cấu hình và gọi "nhạc trưởng" Compose. (Do hôm trước đã dùng cờ `--build` rồi, hôm nay chỉ cần chạy lệnh `up` bình thường, hệ thống sẽ bật lên chỉ trong 1-2 giây).

```bash
# Đi tới thư mục chứa file docker-compose.yml
cd ~/beniot_dev/BPURD-BeniotPhanUltimateRobotDog/pi4-ws/camera-astra-pro-ws

# Khởi động ngầm container
docker compose up -d

```

**Bước 3: Kiểm tra luồng dữ liệu (Nghiệm thu)**
Kiểm tra xem hệ thống đã "mở mắt" thành công chưa bằng cách xem log:

```bash
docker logs -f astra_pro_humble

```

*(Bấm `Ctrl + C` để thoát màn hình log khi thấy dòng chữ `device started.`)*

Cuối cùng, kiểm tra tốc độ khung hình (FPS) của luồng Depth 3D truyền ra Host:

```bash
ros2 topic hz /camera/depth/image_raw

```

*(Nếu terminal nhảy số ổn định quanh mức `rate: 30.000`, hệ thống đã sẵn sàng 100% cho các thuật toán Sensor Fusion!)*

---

### 💡 Lưu ý quan trọng về Cáp cắm

* Luôn đảm bảo Astra Pro được cắm trực tiếp vào **cổng USB 3.0 (Xanh dương)** trên mạch Pi 4.
* Nếu chạy đồng thời Lidar, hãy cắm Lidar vào cổng USB 2.0 (Đen) hoặc dùng Hub có nguồn phụ để tránh tình trạng sụt áp nguồn điện của mạch Pi gây lỗi `statusCode: 8`.

======================= CÁCH CLONE VÀ CHẠY VỀ MÁY KHÁC
Chào cậu, Astra Pro đây! Nghe cậu nói "mừng quá" mà tôi cũng vui lây! Câu hỏi này của cậu chạm đúng vào giá trị cốt lõi đắt giá nhất của Docker: **Viết một lần, chạy mọi nơi (Write once, run anywhere).**

Chính nhờ kiến trúc phần mềm tuyệt vời này, dự án BPURD của cậu giờ đây đã sở hữu tính di động (portability) hoàn hảo. Dù hệ điều hành Host của Pi 5 là Ubuntu 24.04 (Jazzy) hay Nvidia Jetson chạy JetPack OS, thì lõi CPU của chúng đều dùng kiến trúc **ARM64**. Do đó, "bản thiết kế" Docker của chúng ta sẽ lắp ráp ra một môi trường ROS 2 Humble giống hệt nhau trên mọi thiết bị mà không cần sửa một dòng code nào!

Để team AirAware có thể mang thư mục này đi chinh chiến trên mọi bo mạch, cậu hãy tạo thêm một file tên là `DEPLOYMENT_GUIDE.md` (Hướng dẫn triển khai đa nền tảng) và dán nội dung chuẩn chỉnh dưới đây vào nhé:

---

# 🌍 Hướng Dẫn Triển Khai Astra Pro Lên Đa Thiết Bị Nhúng (Pi 4, Pi 5, Jetson)

Kiến trúc này sử dụng Docker. Điều này có nghĩa là hệ điều hành gốc (Host OS) không còn quan trọng. Chỉ cần bo mạch dùng chip ARM64 (aarch64) và có cài đặt Docker, toàn bộ hệ sinh thái ROS 2 Humble của Astra Pro sẽ tự động được xây dựng hoàn chỉnh chỉ với 1 lệnh duy nhất.

## Giai Đoạn 1: Chuẩn bị máy mới (Chỉ làm 1 lần duy nhất)

Khi cầm một bo mạch Pi 5 hoặc Jetson hoàn toàn mới, bạn chỉ cần đảm bảo máy có mạng Internet và cài đặt 2 công cụ nền tảng là Git và Docker.

**Cài đặt Docker trên bo mạch nhúng (Ubuntu/Debian):**
Mở terminal của máy mới và chạy lần lượt các lệnh sau:

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt Git
sudo apt install git -y

# 3. Cài đặt Docker tự động qua script chính thức
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Cấp quyền cho user hiện tại dùng Docker không cần gõ sudo
sudo usermod -aG docker $USER

```

*(Lưu ý: Sau khi chạy lệnh 4, bạn cần **Log out (đăng xuất)** khỏi máy và Log in lại để quyền Docker có hiệu lực).*

---

## Giai Đoạn 2: Clone Code và Vận hành (Vòng lặp hằng ngày)

### Bước 1: Kéo toàn bộ chất xám về máy

Mở terminal tại thư mục làm việc mong muốn và clone kho chứa mã nguồn dự án:

```bash
# Clone repository
git clone https://github.com/Ben-RobAIoT/BPURD-BeniotPhanUltimateRobotDog.git

# Di chuyển vào thư mục cấu hình của Astra Pro
cd BPURD-BeniotPhanUltimateRobotDog/pi4-ws/camera-astra-pro-ws

```

### Bước 2: Thiết lập Tối ưu Phần cứng (Hardware Bypass)

Bất kể là Pi 4, Pi 5 hay Jetson, bạn cần dọn đường để phần mềm trong Docker giao tiếp trực tiếp với cổng USB:

```bash
# 1. Tạm tắt driver UVC của hệ điều hành Host để chống tranh chấp quyền điều khiển
sudo rmmod uvcvideo

# 2. Mở rộng băng thông USB lên 1000MB (Quan trọng nhất với dòng Raspberry Pi)
sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'

```

*(Ghi chú cho Jetson: Cổng USB của Nvidia Jetson có chip điều khiển mạnh hơn Pi, ít khi bị nghẽn `statusCode: 1004`, nhưng việc chạy lệnh mở rộng bộ nhớ này vẫn rất an toàn và được khuyến nghị).*

### Bước 3: Đánh thức hệ sinh thái Docker

Vì là lần chạy đầu tiên trên máy mới, bạn cần thêm cờ `--build` để Docker tự động đọc file `Dockerfile`, tải mã nguồn Orbbec, tự cài thư viện C++ và tự build gói ROS 2:

```bash
docker compose up -d --build

```

*(Quá trình build trên Pi 5 hoặc Jetson Orin sẽ nhanh hơn rất nhiều so với Pi 4, chỉ mất khoảng 2-3 phút).*

### Bước 4: Nghiệm thu thành quả

Kiểm tra xem camera Astra Pro đã phát tia hồng ngoại và truyền ảnh chưa:

```bash
# Xem log hệ thống (Thấy chữ 'device started.' là thành công)
docker logs -f astra_pro_humble

# Mở terminal mới, kiểm tra FPS của luồng ảnh 3D
ros2 topic hz /camera/depth/image_raw

```

---

## 🛠️ Xử lý sự cố khi đổi máy

* **Lỗi "exec format error" trên Docker:** Xảy ra nếu bạn cố đem bộ code này chạy trên máy tính xách tay (Laptop dùng chip Intel/AMD x86_64). Dockerfile này được thiết lập `platform: linux/arm64` dành riêng cho hệ sinh thái máy tính nhúng (Pi, Jetson).
* **Jetson không nhận thiết bị USB:** Đảm bảo cáp cấp nguồn cho Jetson đủ công suất (thường là nguồn DC 5V-4A), nếu dùng nguồn sạc điện thoại yếu, Jetson sẽ tự động ngắt cổng USB để bảo vệ bo mạch.

---

Cậu hãy gom file `DEPLOYMENT_GUIDE.md` này chung với file `README.md` lúc nãy và `git push` lên nhánh `main` nhé. Sự nghiệp phát triển phần mềm nhúng của cậu chính thức bước sang một trang mới cực kỳ gọn gàng và tự động hóa cao rồi đấy! Cậu có muốn tôi hướng dẫn thêm cách đồng bộ cả múi giờ (Timezone) của máy Host vào trong Docker để sau này lưu file log cho chuẩn thời gian không?