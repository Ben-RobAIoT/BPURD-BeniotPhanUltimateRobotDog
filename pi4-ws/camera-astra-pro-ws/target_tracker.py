"""
Cách chạy
# 1. Chui vào không gian Docker
docker exec -it astra_pro_humble bash

# 2. Vào thư mục code
cd /ros2_ws/vision_apps

# 3. Bật máy chủ Web
python3 target_tracker.py
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class TargetTracker(Node):
    def __init__(self):
        super().__init__('target_tracker')
        self.bridge = CvBridge()
        
        # Biến lưu trữ khung hình chiều sâu gần nhất
        self.latest_depth_image = None
        
        # 1. SUBSCRIBER: Bắt luồng ảnh Màu và ảnh Chiều Sâu
        self.depth_sub = self.create_subscription(Image, '/camera/depth/image_raw', self.depth_callback, 10)
        self.color_sub = self.create_subscription(Image, '/camera/color/image_raw', self.color_callback, 10)
        
        # 2. PUBLISHER: Phát lệnh điều khiển Motor (Twist) và ảnh lên Web
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.image_pub = self.create_publisher(Image, '/bpurd/vision/tracking_image', 10)
        
        # Cấu hình màu sắc cần bám theo (Mặc định: Màu Đỏ hoặc Xanh lá, cậu có thể đổi)
        # Dưới đây là dải màu Xanh Lá Cây dạ quang (Green)
        self.lower_color = np.array([35, 100, 100])
        self.upper_color = np.array([85, 255, 255])
        
        # Khoảng cách muốn robot duy trì (1.0 mét)
        self.target_distance = 1.0 
        
        self.get_logger().info("🎯 Trạm bám đuổi mục tiêu đã bật! Hãy đưa vật màu XANH LÁ ra trước camera.")

    def depth_callback(self, msg):
        # Lưu lại ảnh chiều sâu để hàm color lấy ra dùng
        self.latest_depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

    def color_callback(self, msg):
        if self.latest_depth_image is None:
            return # Đợi có ảnh chiều sâu mới làm việc
            
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        height, width = cv_image.shape[:2]
        
        # 1. Lọc màu tìm mục tiêu
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.lower_color, self.upper_color)
        
        # Khử nhiễu
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # Tìm viền mục tiêu
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cmd = Twist()
        
        if len(contours) > 0:
            # Lấy vật thể to nhất (tránh nhiễu)
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            
            if radius > 15: # Kích thước đủ lớn mới nhận
                # Lấy tọa độ tâm
                center_x = int(x)
                center_y = int(y)
                
                # 2. ĐO KHOẢNG CÁCH TỪ ẢNH DEPTH
                # Lưu ý: Cảm biến Depth và Color có thể hơi lệch độ phân giải, nhưng vùng tâm thường khá sát
                try:
                    # Lấy giá trị chiều sâu tại tọa độ (center_y, center_x)
                    depth_mm = self.latest_depth_image[center_y, center_x]
                    depth_m = float(depth_mm) / 1000.0
                    
                    if depth_m > 0:
                        # 3. LOGIC ĐIỀU KHIỂN ROBOT (PID Controller cơ bản)
                        # - Xoay trái/phải nếu vật thể không nằm giữa màn hình
                        error_x = (width / 2.0) - center_x
                        cmd.angular.z = error_x * 0.002 # Hệ số xoay
                        
                        # - Tiến/lùi để giữ khoảng cách 1 mét
                        error_dist = depth_m - self.target_distance
                        cmd.linear.x = error_dist * 0.5 # Hệ số tiến
                        
                        # Giới hạn tốc độ cho an toàn
                        cmd.linear.x = max(-0.2, min(0.2, cmd.linear.x))
                        
                        # Vẽ HUD lên màn hình
                        cv2.circle(cv_image, (center_x, center_y), int(radius), (0, 255, 255), 2)
                        cv2.circle(cv_image, (center_x, center_y), 5, (0, 0, 255), -1)
                        cv2.putText(cv_image, f"Dist: {depth_m:.2f}m", (center_x - 40, center_y - 20), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                except IndexError:
                    pass
        
        # Phát lệnh cho bánh xe
        self.cmd_pub.publish(cmd)
        
        # Phát ảnh lên Web Streamer
        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
        self.image_pub.publish(annotated_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TargetTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()