"""
Cách chạy
# 1. Chui vào không gian Docker
docker exec -it astra_pro_humble bash

# 2. Vào thư mục code
cd /ros2_ws/vision_apps

# 3. Bật máy chủ Web
python3 pointcloud_exporter.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String
import sensor_msgs_py.point_cloud2 as pc2

class PointCloudExporter(Node):
    def __init__(self):
        super().__init__('pointcloud_exporter')
        
        # 1. SUBSCRIBER: Bắt luồng mây điểm 3D từ camera
        self.subscription = self.create_subscription(
            PointCloud2,
            '/camera/depth/points',
            self.pc_callback,
            10
        )
        
        # 2. PUBLISHER: Báo cáo trạng thái sau khi đã kết xuất xong file
        self.status_pub = self.create_publisher(String, '/bpurd/vision/pc_status', 10)
        
        # 3. Biến trạng thái (State)
        self.is_saved = False # Cờ đánh dấu để chỉ lấy 1 khung hình, tránh nổ RAM Pi 4
        
        # Tên file xuất ra (sẽ nằm cùng thư mục code của cậu)
        self.output_filename = "static_environment.ply"
        
        self.get_logger().info("☁️ Trạm xuất Point Cloud đã bật. Đang chờ quét 3D...")

    def pc_callback(self, msg):
        # Nếu đã lưu xong thì bỏ qua các frame sau để CPU nghỉ ngơi
        if self.is_saved:
            return
            
        self.get_logger().info("Đang bóc tách điểm 3D... Vui lòng giữ camera đứng im!")
        
        try:
            # Dùng công cụ lõi của ROS 2 để đọc tọa độ (X, Y, Z), bỏ qua các điểm bị nhiễu (NaN)
            points = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))
            
            if len(points) == 0:
                self.get_logger().warn("Không có điểm hợp lệ, chờ khung hình tiếp theo...")
                return

            # Gọi hàm tự viết để lưu thành file chuẩn công nghiệp .ply
            self.save_to_ply(points, self.output_filename)
            self.is_saved = True
            
            # Đóng gói và phát thông báo "Hoàn thành" ra Topic
            success_msg = String()
            success_msg.data = f"SUCCESS|{len(points)}|{self.output_filename}"
            self.status_pub.publish(success_msg)
            
            self.get_logger().info(f"✅ HOÀN TẤT! Đã quét thành công {len(points)} điểm không gian.")
            self.get_logger().info(f"File đã được lưu tại: {self.output_filename}")
            self.get_logger().info("Vui lòng ấn Ctrl+C để thoát.")
            
        except Exception as e:
            self.get_logger().error(f"Lỗi xử lý mây điểm: {e}")

    def save_to_ply(self, points, filename):
        """
        Thuật toán ghi file PLY chuẩn ASCII.
        Không cần thư viện bên thứ 3, chạy cực nhanh và an toàn trên kiến trúc ARM.
        """
        with open(filename, 'w') as f:
            # Phần Header khai báo cấu trúc cho phần mềm 3D đọc hiểu
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("end_header\n")
            
            # Phần Body: Đổ toàn bộ tọa độ điểm ảnh vào
            for p in points:
                f.write(f"{p[0]} {p[1]} {p[2]}\n")

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudExporter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()