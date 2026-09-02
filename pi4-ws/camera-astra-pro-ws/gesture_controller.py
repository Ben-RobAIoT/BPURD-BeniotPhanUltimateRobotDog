"""
Cách chạy
# 1. Chui vào không gian Docker
docker exec -it astra_pro_humble bash

# 2. Vào thư mục code
cd /ros2_ws/vision_apps

# 3. Bật máy chủ Web
python3 gesture_cntroller.py

"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

# Kéo thư viện cá nhân của cậu vào
from gesture_library import GestureDictionary

class HandGestureController(Node):
    def __init__(self):
        super().__init__('hand_gesture_controller')
        self.bridge = CvBridge()
        
        # 1. Gọi Class "Từ điển" ra
        self.brain = GestureDictionary()
        
        # 2. SUBSCRIBER
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10
        )
        
        # 3. PUBLISHERS
        self.cmd_pub = self.create_publisher(String, '/bpurd/control/gesture_cmd', 10)
        self.image_pub = self.create_publisher(Image, '/bpurd/vision/gesture_image', 10)
        
        self.get_logger().info("✋ Hệ thống cử chỉ (Đã tách Library) sẵn sàng!")

    def image_callback(self, msg):
        try:
            # 1. Chuyển ảnh ROS -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            
            # 2. Đưa ảnh vào thư viện để nó tự nhận diện và vẽ
            # Trả về mã lệnh (STOP/FORWARD) và bức ảnh đã vẽ xương
            cmd_data, annotated_image = self.brain.process_and_recognize(cv_image)
            
            # 3. Phát Lệnh & Vẽ HUD
            if cmd_data != "NONE":
                # In lệnh lên màn hình để dễ xem trên Web
                text_color = (0, 0, 255) if cmd_data == "STOP" else (0, 255, 0)
                cv2.putText(
                    annotated_image, 
                    f"CMD: {cmd_data}", 
                    (20, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, text_color, 4, cv2.LINE_AA
                )
                
                # Bắn lệnh chữ ra Topic
                cmd_msg = String()
                cmd_msg.data = cmd_data
                self.cmd_pub.publish(cmd_msg)
                
            # 4. Chuyển ảnh OpenCV -> ROS và phát lên Topic cho Web Streamer
            out_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding="bgr8")
            self.image_pub.publish(out_msg)
                
        except Exception as e:
            self.get_logger().error(f"Lỗi hệ thống: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = HandGestureController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()