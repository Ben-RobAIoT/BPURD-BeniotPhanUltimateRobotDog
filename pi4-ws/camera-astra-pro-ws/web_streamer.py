"""
# 1. Chui vào không gian Docker
docker exec -it astra_pro_humble bash

# 2. Vào thư mục code
cd /ros2_ws/vision_apps

# 3. Bật máy chủ Web
python3 web_streamer.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from flask import Flask, Response
import threading

# Khởi tạo Flask App
app = Flask(__name__)
# Biến toàn cục lưu frame ảnh mới nhất
latest_frame = None

class WebStreamerNode(Node):
    def __init__(self):
        super().__init__('web_streamer_node')
        self.bridge = CvBridge()
        
        # Subscribe vào luồng ảnh màu
        self.subscription = self.create_subscription(
            Image,
            '/bpurd/vision/tracking_image',
            self.image_callback,
            10
        )
        self.get_logger().info("🌐 Web Streamer đã sẵn sàng! Mở trình duyệt: http://<IP-Của-Pi>:5000/video_feed")

    def image_callback(self, msg):
        global latest_frame
        try:
            # Chuyển ROS Image thành OpenCV Image
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            # Mã hóa ảnh thành chuẩn JPEG để truyền qua web
            ret, buffer = cv2.imencode('.jpg', cv_image)
            if ret:
                latest_frame = buffer.tobytes()
        except Exception as e:
            self.get_logger().error(f"Lỗi: {e}")

# Hàm tạo luồng video cho Flask (MJPEG Streaming)
def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main(args=None):
    rclpy.init(args=args)
    node = WebStreamerNode()
    
    # Chạy Flask ở một Thread (luồng) riêng biệt để không chặn ROS 2
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()