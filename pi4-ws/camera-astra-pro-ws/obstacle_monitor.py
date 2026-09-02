import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String, Float32
from cv_bridge import CvBridge
import cv2
import numpy as np

class ObstacleMonitor(Node):
    def __init__(self):
        super().__init__('obstacle_monitor_node')
        
        # 1. Khởi tạo công cụ chuyển đổi ảnh ROS sang OpenCV
        self.bridge = CvBridge()
        self.min_safe_distance = 0.5 # 0.5 mét
        
        # 2. SUBSCRIBER: Lấy dữ liệu raw từ camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10
        )
        
        # 3. PUBLISHER: Đẩy dữ liệu đã xử lý ra custom topic cho hệ thống khác dùng
        self.distance_pub = self.create_publisher(Float32, '/bpurd/vision/front_distance', 10)
        self.alert_pub = self.create_publisher(String, '/bpurd/vision/obstacle_alert', 10)
        
        self.get_logger().info("Khoang 1: Hệ thống cảnh báo va chạm 3D đã sẵn sàng!")

    def depth_callback(self, msg):
        try:
            # Chuyển đổi message ROS sang ảnh ma trận numpy (16-bit depth)
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            
            # Lấy kích thước ảnh
            height, width = cv_image.shape
            
            # Chọn vùng trung tâm (Region of Interest - ROI) - kích thước 100x100 pixel
            center_x, center_y = width // 2, height // 2
            roi = cv_image[center_y-50:center_y+50, center_x-50:center_x+50]
            
            # Loại bỏ các giá trị 0 (điểm mù/không đo được) để tính toán chính xác
            valid_depths = roi[roi > 0]
            
            if len(valid_depths) > 0:
                # Tính khoảng cách trung bình (camera thường trả về mm)
                avg_distance_mm = np.mean(valid_depths)
                avg_distance_m = avg_distance_mm / 1000.0
                
                # Publish khoảng cách liên tục
                self.distance_pub.publish(Float32(data=avg_distance_m))
                
                # Xử lý Logic Cảnh báo
                if avg_distance_m < self.min_safe_distance:
                    alert_msg = String()
                    alert_msg.data = f"DANGER: Vật cản phía trước {avg_distance_m:.2f}m!"
                    self.alert_pub.publish(alert_msg)
                    self.get_logger().warn(alert_msg.data)
                    
        except Exception as e:
            self.get_logger().error(f"Lỗi xử lý ảnh: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleMonitor()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()