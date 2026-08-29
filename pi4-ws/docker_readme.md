Author: Beniot-Phan

## 1. Nhóm quản lý IMAGE

### `docker pull`
**Định nghĩa**: Tải image từ registry (Docker Hub mặc định) về máy local.
```bash
docker pull <image>:<tag>
docker pull ubuntu:24.04
docker pull ros:humble
```

### `docker build`
**Định nghĩa**: Build image mới từ file `Dockerfile`.
```bash
docker build -t <ten_image>:<tag> <đường_dẫn_context>
docker build -t robot-dog:v1 .
docker build -t robot-dog:v1 -f Dockerfile.dev .   # chỉ định file Dockerfile khác tên mặc định
docker build --no-cache -t robot-dog:v1 .          # build lại từ đầu, không dùng cache layer
```

### `docker images` (hoặc `docker image ls`)
**Định nghĩa**: Liệt kê tất cả image đang có trên máy.
```bash
docker images
docker images -a          # gồm cả image trung gian (intermediate)
docker images --filter "dangling=true"   # chỉ image "rác" (không tag, không dùng)
```

### `docker rmi`
**Định nghĩa**: Xóa 1 hoặc nhiều image theo ID/tên.
```bash
docker rmi <image_id>
docker rmi robot-dog:v1
docker rmi -f <image_id>     # ép xóa dù đang có container dùng
```

### `docker tag`
**Định nghĩa**: Gán thêm tên/tag khác cho 1 image đã có (thường dùng trước khi push lên registry).
```bash
docker tag robot-dog:v1 myrepo/robot-dog:latest
```

### `docker push`
**Định nghĩa**: Đẩy image lên registry (Docker Hub, GHCR, private registry...).
```bash
docker push myrepo/robot-dog:latest
```

### `docker history`
**Định nghĩa**: Xem lịch sử các layer đã tạo nên 1 image (debug xem layer nào nặng).
```bash
docker history robot-dog:v1
```

### `docker save` / `docker load`
**Định nghĩa**: Xuất image ra file `.tar` (để copy qua máy khác không có mạng) và nạp lại.
```bash
docker save -o robot-dog.tar robot-dog:v1
docker load -i robot-dog.tar
```

---

## 2. Nhóm quản lý CONTAINER

### `docker run`
**Định nghĩa**: Tạo và chạy container mới từ 1 image.
```bash
docker run <image>
docker run -d --name robot_sim robot-dog:v1        # -d: chạy nền (detached)
docker run -it ubuntu:24.04 bash                    # -it: tương tác terminal
docker run -p 8080:80 nginx                         # map port host:container
docker run -v /host/path:/container/path robot-dog:v1  # mount volume
docker run --rm robot-dog:v1                        # tự xóa container khi dừng
docker run --gpus all robot-dog:v1                  # cấp GPU (cần NVIDIA Container Toolkit)
docker run --network host robot-dog:v1              # dùng chung network với host
docker run --device=/dev/ttyUSB0 robot-dog:v1       # cho container truy cập thiết bị phần cứng (Lidar, USB...)
docker run -e VAR_NAME=value robot-dog:v1           # truyền biến môi trường
```
> Đây là lệnh quan trọng nhất — kết hợp nhiều flag tùy nhu cầu (network, volume, device, env...).

### `docker ps`
**Định nghĩa**: Liệt kê container đang chạy.
```bash
docker ps
docker ps -a          # gồm cả container đã dừng
docker ps -q          # chỉ in ID (hay dùng kết hợp lệnh khác)
```

### `docker stop` / `docker start` / `docker restart`
**Định nghĩa**: Dừng / khởi động lại / restart container đang tồn tại (không xóa).
```bash
docker stop robot_sim
docker start robot_sim
docker restart robot_sim
```

### `docker kill`
**Định nghĩa**: Dừng container ngay lập tức (gửi SIGKILL, khác với `stop` gửi SIGTERM trước rồi mới kill).
```bash
docker kill robot_sim
```

### `docker rm`
**Định nghĩa**: Xóa container (phải dừng trước, hoặc dùng `-f`).
```bash
docker rm robot_sim
docker rm -f robot_sim         # ép xóa dù đang chạy
docker container prune         # xóa hết container đã dừng
```

### `docker exec`
**Định nghĩa**: Chạy thêm 1 lệnh/mở terminal mới bên trong container đang chạy.
```bash
docker exec -it robot_sim bash
docker exec robot_sim ls /app
```

### `docker logs`
**Định nghĩa**: Xem log output (stdout/stderr) của container.
```bash
docker logs robot_sim
docker logs -f robot_sim         # follow, xem real-time giống tail -f
docker logs --tail 100 robot_sim # chỉ xem 100 dòng cuối
```

### `docker attach`
**Định nghĩa**: Gắn terminal hiện tại vào tiến trình chính (PID 1) của container đang chạy (khác `exec` vì không tạo tiến trình mới).
```bash
docker attach robot_sim
```
> Thoát bằng `Ctrl+P, Ctrl+Q` để không làm container bị dừng.

### `docker inspect`
**Định nghĩa**: Xem thông tin chi tiết (JSON) của container/image/volume/network (IP, mount, config...).
```bash
docker inspect robot_sim
docker inspect -f '{{.NetworkSettings.IPAddress}}' robot_sim   # lọc field cụ thể
```

### `docker cp`
**Định nghĩa**: Copy file/thư mục giữa host và container.
```bash
docker cp robot_sim:/app/log.txt ./log.txt
docker cp ./config.yaml robot_sim:/app/config.yaml
```

### `docker stats`
**Định nghĩa**: Xem tài nguyên CPU/RAM/Network container đang dùng theo thời gian thực (giống `top`).
```bash
docker stats
docker stats robot_sim
```

### `docker rename`
**Định nghĩa**: Đổi tên container.
```bash
docker rename robot_sim robot_sim_v2
```

### `docker pause` / `docker unpause`
**Định nghĩa**: Tạm dừng toàn bộ tiến trình trong container (đóng băng) mà không dừng hẳn.
```bash
docker pause robot_sim
docker unpause robot_sim
```

---

## 3. Nhóm quản lý VOLUME (lưu trữ dữ liệu bền vững)

### `docker volume create`
**Định nghĩa**: Tạo volume để lưu dữ liệu độc lập với vòng đời container.
```bash
docker volume create robot_data
```

### `docker volume ls`
**Định nghĩa**: Liệt kê volume hiện có.
```bash
docker volume ls
```

### `docker volume inspect`
**Định nghĩa**: Xem chi tiết volume (đường dẫn thật trên host).
```bash
docker volume inspect robot_data
```

### `docker volume rm` / `docker volume prune`
**Định nghĩa**: Xóa 1 volume / xóa hết volume không dùng đến.
```bash
docker volume rm robot_data
docker volume prune
```

---

## 4. Nhóm quản lý NETWORK

### `docker network ls`
**Định nghĩa**: Liệt kê các network (bridge, host, none, custom...).
```bash
docker network ls
```

### `docker network create`
**Định nghĩa**: Tạo network riêng để các container giao tiếp với nhau qua tên (DNS nội bộ).
```bash
docker network create robot_net
docker network create --driver bridge robot_net
```

### `docker network connect` / `disconnect`
**Định nghĩa**: Gắn/gỡ container khỏi 1 network.
```bash
docker network connect robot_net robot_sim
docker network disconnect robot_net robot_sim
```

### `docker network inspect` / `rm`
```bash
docker network inspect robot_net
docker network rm robot_net
```

---

## 5. Nhóm DOCKER COMPOSE (quản lý nhiều container cùng lúc)

### `docker compose up`
**Định nghĩa**: Đọc file `docker-compose.yml`, tạo và chạy toàn bộ service khai báo.
```bash
docker compose up
docker compose up -d              # chạy nền
docker compose up --build         # build lại image trước khi chạy
```

### `docker compose down`
**Định nghĩa**: Dừng và xóa toàn bộ container/network do compose tạo ra.
```bash
docker compose down
docker compose down -v            # xóa luôn cả volume
```

### `docker compose ps` / `logs` / `exec`
**Định nghĩa**: Tương tự bản đơn lẻ nhưng áp dụng cho toàn bộ hệ service trong compose.
```bash
docker compose ps
docker compose logs -f
docker compose exec <service_name> bash
```

### `docker compose restart` / `stop` / `start`
```bash
docker compose restart <service_name>
docker compose stop
docker compose start
```

### `docker compose build`
**Định nghĩa**: Chỉ build image mà không chạy.
```bash
docker compose build
```

---

## 6. Nhóm HỆ THỐNG & DỌN DẸP

### `docker system df`
**Định nghĩa**: Xem dung lượng ổ đĩa Docker đang chiếm (image, container, volume, cache).
```bash
docker system df
```

### `docker system prune`
**Định nghĩa**: Dọn dẹp toàn bộ rác (container dừng, network không dùng, image dangling, build cache).
```bash
docker system prune
docker system prune -a            # xóa luôn cả image không dùng bởi container nào
docker system prune -a --volumes  # xóa luôn cả volume không dùng (CẨN THẬN, mất data)
```

### `docker info`
**Định nghĩa**: Xem thông tin cấu hình tổng thể của Docker Engine đang chạy.
```bash
docker info
```

### `docker version`
**Định nghĩa**: Xem phiên bản Docker Client/Server.
```bash
docker version
```

---

## 7. Nhóm ĐĂNG NHẬP / REGISTRY

### `docker login` / `docker logout`
**Định nghĩa**: Đăng nhập/đăng xuất tài khoản Docker Hub hoặc private registry.
```bash
docker login
docker login myregistry.com
docker logout
```

---

## 8. Dockerfile — các chỉ thị hay dùng khi viết image (không phải lệnh CLI nhưng đi kèm `build`)

| Chỉ thị | Định nghĩa |
|---|---|
| `FROM` | Chọn image nền (base image) |
| `WORKDIR` | Đặt thư mục làm việc mặc định trong container |
| `COPY` / `ADD` | Copy file từ host vào image |
| `RUN` | Chạy lệnh lúc build image (cài đặt package...) |
| `ENV` | Đặt biến môi trường mặc định |
| `EXPOSE` | Khai báo port container sẽ dùng (chỉ mang tính document, không tự map) |
| `CMD` | Lệnh mặc định chạy khi container start (có thể bị override khi `docker run ... <cmd>`) |
| `ENTRYPOINT` | Lệnh cố định chạy khi container start (khó override hơn `CMD`) |
| `VOLUME` | Khai báo thư mục cần persist dữ liệu |
| `ARG` | Biến chỉ dùng lúc build, không tồn tại lúc runtime |

---

## 9. Bảng flag hay dùng chung (áp dụng nhiều lệnh)

| Flag | Ý nghĩa |
|---|---|
| `-d` | Detached — chạy nền |
| `-it` | Interactive + TTY — mở terminal tương tác |
| `-p host:container` | Map cổng |
| `-v host:container` | Mount volume/thư mục |
| `--name` | Đặt tên container |
| `--rm` | Tự xóa container khi dừng |
| `-e` | Set biến môi trường |
| `-f` | Force (ép buộc) |
| `--network` | Chỉ định network |
| `--gpus` | Cấp GPU cho container |
| `--device` | Cho container truy cập thiết bị phần cứng host |

---
