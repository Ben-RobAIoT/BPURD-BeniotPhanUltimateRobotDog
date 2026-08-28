import os
import subprocess
import cv2
import numpy as np
import threading
import time
from flask import Flask, Response

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage # ĐỔI IMPORT Ở ĐÂY

app = Flask(__name__)
current_frame_bgr = None 

class CameraRosNode(Node):
    def __init__(self):
        super().__init__('fdamr_camera_node')
        # SỬA KIỂU DỮ LIỆU VÀ TÊN TOPIC THÊM CHỮ /compressed
        self.publisher_ = self.create_publisher(CompressedImage, '/camera/image_raw/compressed', 10)
        self.get_logger().info("Đã khởi tạo ROS 2 Publisher cho Camera Pi V3 (Dạng Nén)")

    def publish_frame(self, frame_bgr):
        # TỰ CHỦ ĐỘNG NÉN ẢNH THÀNH JPEG ĐỂ TIẾT KIỆM BĂNG THÔNG
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_link"
        msg.format = "jpeg"
        
        # Nén JPEG chất lượng 50
        ret, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 50])
        msg.data = buffer.tobytes()
        
        self.publisher_.publish(msg)

def read_exactly(pipe, size):
    data = b''
    while len(data) < size:
        chunk = pipe.read(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def camera_capture_loop(ros_node):
    global current_frame_bgr
    
    cmd = [
        "gst-launch-1.0", "-q",
        "libcamerasrc", "!",
        "video/x-raw,width=640,height=480,framerate=20/1", "!",
        "videoconvert", "!",
        "video/x-raw,format=RGB", "!",
        "fdsink", "fd=1"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frame_size = 640 * 480 * 3 

    try:
        while rclpy.ok():
            raw_data = read_exactly(process.stdout, frame_size)
            if not raw_data:
                ros_node.get_logger().error("Luồng camera bị ngắt.")
                break

            frame = np.frombuffer(raw_data, dtype=np.uint8).reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 1. Ưu tiên số 1: Đẩy dữ liệu siêu tốc cho ROS 2
            ros_node.publish_frame(frame_bgr)

            # 2. Cập nhật biến toàn cục bằng ảnh thô (không tốn CPU nén ảnh ở đây)
            current_frame_bgr = frame_bgr

    finally:
        process.terminate()

def generate_frames_for_flask():
    global current_frame_bgr
    while True:
        if current_frame_bgr is not None:
            # Tối ưu: Chỉ thực sự nén JPEG khi có người đang xem qua IP HTTP
            # Giảm chất lượng xuống 50 để truyền mạng cục bộ mượt hơn
            ret, buffer = cv2.imencode('.jpg', current_frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 50])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Nhường CPU cho luồng ROS 2 hoạt động (Khoảng 15-20fps cho web là quá đủ để quan sát)
        time.sleep(0.05) 

@app.route('/')
def video_feed():
    return Response(generate_frames_for_flask(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000, threaded=True)

def main(args=None):
    rclpy.init(args=args)
    ros_node = CameraRosNode()

    capture_thread = threading.Thread(target=camera_capture_loop, args=(ros_node,))
    capture_thread.daemon = True
    capture_thread.start()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        rclpy.spin(ros_node)
    except KeyboardInterrupt:
        pass
    finally:
        ros_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    print("========== HỆ THỐNG MẮT THẦN ĐÃ SẴN SÀNG ==========")
    print("- Đang phát ROS Topic: /camera/image_raw")
    print("- Đang phát HTTP IP: http://<IP>:5000")
    print("===================================================")
    main()