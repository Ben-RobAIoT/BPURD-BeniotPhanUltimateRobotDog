#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist  # Thư viện để gửi lệnh điều khiển động cơ
import cv2
import numpy as np
import time

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

class LiveTestTFLiteNode(Node):
    def __init__(self):
        super().__init__('live_test_tflite_node')
        
        self.subscription = self.create_subscription(
            CompressedImage, '/camera/image_raw/compressed', self.image_callback, 10)
        
        self.annotated_img_pub = self.create_publisher(
            CompressedImage, '/camera/test_annotated/compressed', 10)
            
        # TẠO PUBLISHER ĐỂ GỬI LỆNH DỪNG XE XUỐNG ESP32
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info("✅ Đã bật Node Test TFLite (Bản nâng cấp có Phanh khẩn cấp)!")
        
        # ==========================================
        # ⚙️ KHU VỰC CẤU HÌNH KHOẢNG CÁCH (Tùy chỉnh tại đây)
        # ==========================================
        self.DISTANCE_MAX_VIEW = 3.0   # Quét tối đa 3 mét (xa hơn thì lờ đi)
        self.DISTANCE_WARNING = 1.5    # Dưới 1.5m -> Chuyển màu Cam cảnh báo
        self.DISTANCE_STOP = 0.5       # Dưới 0.5m -> MÀU ĐỎ + KÍCH HOẠT PHANH ESP32
        
        # Load Model
        model_path = "/home/beniot-phan/beniot_dev/FDAMRS_ws/src/camera_pi3/tflite_model/detect.tflite"
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.fy, self.cx, self.cy = 500.0, 320.0, 240.0
        self.camera_height = 0.20  
        
        self.consecutive_frames = 0
        self.CONFIRM_THRESHOLD = 3

    def image_callback(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None: return

        frame_resized = cv2.resize(frame, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

        img_h, img_w, _ = frame.shape
        valid_detection = False
        best_box = None
        best_Z = 0.0

        for i in range(len(scores)):
            if scores[i] > 0.45 and int(classes[i]) == 0:
                ymin, xmin, ymax, xmax = boxes[i]
                x1, y1 = int(xmin * img_w), int(ymin * img_h)
                x2, y2 = int(xmax * img_w), int(ymax * img_h)
                
                if y2 > self.cy + 10:
                    Z = (self.fy * self.camera_height) / (y2 - self.cy)
                    if 0.2 < Z <= self.DISTANCE_MAX_VIEW:
                        valid_detection = True
                        best_box = (x1, y1, x2, y2)
                        best_Z = Z
                        break

        if valid_detection:
            self.consecutive_frames += 1
        else:
            if self.consecutive_frames > 0: self.consecutive_frames -= 1

        # XỬ LÝ LOGIC HIỂN THỊ VÀ ĐIỀU KHIỂN XE
        if best_box:
            x1, y1, x2, y2 = best_box
            if self.consecutive_frames >= self.CONFIRM_THRESHOLD:
                self.consecutive_frames = self.CONFIRM_THRESHOLD + 2
                
                # CHIA VÙNG KHOẢNG CÁCH
                if best_Z <= self.DISTANCE_STOP:
                    # KÍCH HOẠT PHANH KHẨN CẤP
                    stop_msg = Twist()
                    stop_msg.linear.x = 0.0
                    stop_msg.angular.z = 0.0
                    self.cmd_pub.publish(stop_msg)
                    
                    self.get_logger().warn(f"EMERGENCY STOP! Vật cản cách {best_Z:.2f}m")
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3) # Khung Đỏ
                    cv2.putText(frame, f"STOP! {best_Z:.2f}m", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                elif best_Z <= self.DISTANCE_WARNING:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 3) # Khung Cam
                    cv2.putText(frame, f"WARN: {best_Z:.2f}m", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3) # Khung Xanh Lá
                    cv2.putText(frame, f"SAFE: {best_Z:.2f}m", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2) # Xanh lơ chờ lọc Debounce
                cv2.putText(frame, "Filtering...", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        status_color = (0, 255, 0) if self.consecutive_frames >= self.CONFIRM_THRESHOLD else (0, 0, 255)
        cv2.putText(frame, f"Debounce Level: {self.consecutive_frames}/{self.CONFIRM_THRESHOLD}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        success, encoded_image = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        if success:
            out_msg = CompressedImage()
            out_msg.header = msg.header
            out_msg.format = "jpeg"
            out_msg.data = encoded_image.tobytes()
            self.annotated_img_pub.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = LiveTestTFLiteNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()