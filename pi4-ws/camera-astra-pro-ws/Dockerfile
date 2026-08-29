# Sử dụng lõi ROS 2 Humble Base siêu nhẹ
FROM ros:humble-ros-base

# Gom TẤT CẢ thư viện lõi, xử lý video, và C++ vào một lệnh cài đặt duy nhất
RUN apt-get update && apt-get install -y \
    git \
    v4l-utils \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    ros-humble-image-publisher \
    ros-humble-cv-bridge \
    ros-humble-camera-info-manager \
    ros-humble-diagnostic-updater \
    libuvc-dev \
    libusb-1.0-0-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    nlohmann-json3-dev

# Tải bộ mã nguồn ros2_astra_camera nguyên bản
RUN mkdir -p /ros2_ws/src && \
    cd /ros2_ws/src && \
    git clone https://github.com/orbbec/ros2_astra_camera.git

# Tự động quét và cài đặt các thư viện ROS còn sót lại
WORKDIR /ros2_ws
RUN apt-get update && rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y

# Biên dịch toàn bộ gói driver
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

# Tự động nạp môi trường cho mỗi lần chui vào container
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc