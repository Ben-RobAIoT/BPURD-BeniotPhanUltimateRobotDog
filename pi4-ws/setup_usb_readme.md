## 1. Tìm mã định danh (Vendor ID & Product ID) và Cố định cổng USB

Mỗi thiết bị USB đều có một mã "Căn cước công dân" gồm 2 phần: ID của nhà sản xuất (Vendor) và ID của sản phẩm (Product). Để đảm bảo hệ thống không bị nhầm lẫn cổng khi khởi động lại, chúng ta cần cố định chúng.

**Bước 1: Quét thiết bị USB**
Mở terminal trên Pi (sau khi đã cắm Lidar và Astra Pro) và gõ lệnh:

```bash
lsusb

```

Hệ thống sẽ trả về danh sách các thiết bị. Ví dụ kết quả thực tế trên Raspberry Pi 4:

```text
Bus 001 Device 004: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
Bus 001 Device 007: ID 2bc5:0501 Orbbec 3D Technology International, Inc Astra Pro HD Camera
Bus 001 Device 008: ID 2bc5:0403 Orbbec 3D Technology International, Inc Astra Pro

```

> **Nhận xét:**
> * `Silicon Labs`: Đây là driver giao tiếp với LiDAR A1M8 qua cổng USB 2.0.
> * `Orbbec 3D...`: Đây là camera Astra Pro cắm qua cổng USB 3.0. Do là cụm cảm biến phức tạp nên hệ thống nhận diện thành 2 thiết bị độc lập (Camera HD và Cảm biến Depth).
> 
> 

Ghi lại cụm mã (ví dụ: `ID 10c4:ea60`). Trong đó, `10c4` chính là `{idVendor}`, còn `ea60` là `{idProduct}`.

**Bước 2: Viết Script thiết lập (Udev Rules)**
Tạo một file tên là `setup_usb.sh` và cấp quyền thực thi:

```bash
touch setup_usb.sh
chmod +x setup_usb.sh

```

Mở file và dán đoạn mã sau vào (Các mã ID đã được thay thế chính xác từ kết quả `lsusb` ở trên):

```bash
#!/bin/bash
echo "========== BẮT ĐẦU THIẾT LẬP PHẦN CỨNG USB =========="

RULES_CONTENT='
# Cố định cổng cho Lidar A1M8 (chuyển đổi ttyUSB ngẫu nhiên thành /dev/rplidar cố định)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE:="0777", SYMLINK+="rplidar"

# Cấp quyền đọc ghi tối đa cho Orbbec Astra Pro (Phần Camera HD)
SUBSYSTEM=="usb", ATTRS{idVendor}=="2bc5", ATTRS{idProduct}=="0501", MODE:="0777"

# Cấp quyền đọc ghi tối đa cho Orbbec Astra Pro (Phần Depth Sensor)
SUBSYSTEM=="usb", ATTRS{idVendor}=="2bc5", ATTRS{idProduct}=="0403", MODE:="0777"
'

# Ghi trực tiếp các quy tắc này vào lõi hệ điều hành Ubuntu
echo "$RULES_CONTENT" | sudo tee /etc/udev/rules.d/99-robot-usb.rules > /dev/null

# Khởi động lại dịch vụ quản lý thiết bị
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "========== HOÀN TẤT THIẾT LẬP =========="
echo "Kiểm tra Lidar bằng lệnh: ls -l /dev/rplidar"

```

**Bước 3: Chạy Script**
Kích hoạt script bằng lệnh:

```bash
./setup_usb.sh

```
