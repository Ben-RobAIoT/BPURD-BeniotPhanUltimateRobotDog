Tìm xem ID của Docker Humble và Host Jazzy hiện tại có chùng kênh không, phải trùng kênh thì mới giao tiếp được
echo $ROS_DOMAIN_ID => Nếu không ra gì cả thì là mặc định "0" nếu ra số thì chỉnh sửa số đó trong docker-compose.yml để giống nhau nhé (Tùy)

Khởi tạo
docker compose up -d
Bị lỗi
beniot-phan@Beniot-Phan-240405:~/beniot_dev/BPURD-BeniotPhanUltimateRobotDog/pi4-ws/camera-astra-pro-ws$ docker compose up -d
WARN[0000] The "DISPLAY" variable is not set. Defaulting to a blank string. 
WARN[0000] /home/beniot-phan/beniot_dev/BPURD-BeniotPhanUltimateRobotDog/pi4-ws/camera-astra-pro-ws/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock

sửa bằng cáh
sudo usermod -aG docker $USER
newgrp docker

Và chạy lại
docker compose up -d

Thành công thì chạy
docker ps
