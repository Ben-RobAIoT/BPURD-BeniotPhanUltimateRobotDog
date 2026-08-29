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