#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from flask import Flask, Response
import threading
import time

app = Flask(__name__)
current_frame = None

class WebViewerNode(Node):
    def __init__(self):
        super().__init__('web_annotated_viewer_node')
        # Lắng nghe topic có khung đỏ/xanh của TFLite
        self.subscription = self.create_subscription(
            CompressedImage, '/camera/image_annotated/compressed', self.img_callback, 10)

    def img_callback(self, msg):    
        global current_frame
        current_frame = msg.data # Lấy trực tiếp byte ảnh JPEG đã nén

def generate_frames():
    global current_frame
    while True:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytes(current_frame) + b'\r\n')
        time.sleep(0.05)

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def ros_spin(node):
    rclpy.spin(node)

if __name__ == '__main__':
    rclpy.init()
    node = WebViewerNode()
    
    # Chạy ROS 2 ở một luồng riêng
    threading.Thread(target=ros_spin, args=(node,), daemon=True).start()
    
    print("\n" + "="*50)
    print("🌐 SERVER XEM ẢNH AI ĐÃ BẬT!")
    print("👉 Hãy mở trình duyệt trên Laptop/Điện thoại và truy cập:")
    print("   http://<IP_CỦA_PI>:5002")
    print("="*50 + "\n")
    
    # Chạy Flask Server ở cổng 5002 (tránh trùng với stream.py ở cổng 5000)
    app.run(host='0.0.0.0', port=5002, debug=False, use_reloader=False)