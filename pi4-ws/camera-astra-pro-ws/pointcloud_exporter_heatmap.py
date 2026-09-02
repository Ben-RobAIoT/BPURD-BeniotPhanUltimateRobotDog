"""
Cách chạy
# 1. Chui vào không gian Docker
docker exec -it astra_pro_humble bash

# 2. Vào thư mục code
cd /ros2_ws/vision_apps

# 3. Bật máy chủ Web
python3 pointcloud_exporter_heatmap.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String
import sensor_msgs_py.point_cloud2 as pc2
import colorsys # Thư viện chuyển đổi hệ màu (Có sẵn của Python)

class PointCloudExporter(Node):
    def __init__(self):
        super().__init__('pointcloud_exporter')
        
        self.subscription = self.create_subscription(
            PointCloud2,
            '/camera/depth/points',
            self.pc_callback,
            10
        )
        self.status_pub = self.create_publisher(String, '/bpurd/vision/pc_status', 10)
        self.is_saved = False
        self.output_filename = "colored_environment.ply"
        
        self.get_logger().info("☁️ Trạm quét 3D (Có phủ màu Heatmap) đã sẵn sàng...")

    def pc_callback(self, msg):
        if self.is_saved:
            return
            
        self.get_logger().info("Đang bóc tách và phủ màu điểm 3D...")
        
        try:
            points = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))
            
            if len(points) == 0:
                return

            self.save_to_ply_with_color(points, self.output_filename)
            self.is_saved = True
            
            self.get_logger().info(f"✅ HOÀN TẤT! Đã quét {len(points)} điểm.")
            self.get_logger().info(f"File màu lưu tại: {self.output_filename} (Bấm Ctrl+C để thoát)")
            
        except Exception as e:
            self.get_logger().error(f"Lỗi: {e}")

    def save_to_ply_with_color(self, points, filename):
        # 1. Tìm điểm gần nhất và xa nhất để chia tỷ lệ màu
        z_vals = [p[2] for p in points]
        min_z = min(z_vals)
        max_z = max(z_vals)
        # Giới hạn tầm nhìn (Clamp) để màu sắc đẹp hơn (ví dụ: xa tối đa 4 mét)
        if max_z > 4.0: 
            max_z = 4.0
        z_range = max_z - min_z if max_z != min_z else 1.0

        with open(filename, 'w') as f:
            # Cấu trúc Header .ply giờ đây có thêm Khai báo Màu sắc (red, green, blue)
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
            f.write("end_header\n")
            
            # 2. Tính màu và Đổ dữ liệu
            for p in points:
                x, y, z = p[0], p[1], p[2]
                
                # Ép giá trị z vào khoảng min - max đã tính
                z_clamped = max(min_z, min(z, max_z))
                z_norm = (z_clamped - min_z) / z_range
                
                # Chuyển khoảng cách thành màu: Gần (Đỏ) -> Xa (Xanh dương)
                # Dải Hue từ 0.0 (Đỏ) đến 0.66 (Xanh dương)
                hue = 0.66 * z_norm
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                
                # Chuyển đổi về chuẩn 0-255 của bảng màu RGB
                red, green, blue = int(r * 255), int(g * 255), int(b * 255)
                
                # Ghi tọa độ kèm màu sắc
                f.write(f"{x} {y} {z} {red} {green} {blue}\n")

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