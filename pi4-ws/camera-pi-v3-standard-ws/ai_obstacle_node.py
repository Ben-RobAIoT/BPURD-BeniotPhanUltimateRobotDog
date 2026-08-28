#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
import cv2
import numpy as np
import time

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

class AIFusionObstacleNode(Node):
    def __init__(self):
        super().__init__('ai_fusion_obstacle_node')
        
        self.subscription = self.create_subscription(
            CompressedImage, '/camera/image_raw/compressed', self.image_callback, 10)
        self.pc_pub = self.create_publisher(
            PointCloud2, '/camera/virtual_obstacles', 10)
        self.annotated_img_pub = self.create_publisher(
            CompressedImage, '/camera/image_annotated/compressed', 10)
        
        self.get_logger().info("🚀 BẬT TÍNH NĂNG MỞ RỘNG: NÉ NGƯỜI & CHAI NƯỚC (TFLITE)...")
        
        model_path = "/home/beniot-phan/beniot_dev/FDAMRS_ws/src/camera_pi3/tflite_model/detect.tflite"
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        # Thông số xe
        self.fx = 244.44
        self.fy = 300.0
        self.cx = 320.0  
        self.cy = 240.0
        self.camera_height = 0.20
        self.point_density = 0.05
        self.horizon_y = 435.0

        self.consecutive_frames = 0
        self.CONFIRM_THRESHOLD = 3
        self.last_pc = []
        self.last_bboxes = []
        self.prev_time = time.time()

        # ==========================================
        # 🧠 TỪ ĐIỂN CÁC VẬT CẢN CẦN NÉ
        # ==========================================
        self.target_classes = {
            0: 'Person', 
            # 39: 'Bottle',
            56: 'Chair'
        }

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
        current_valid_bboxes = []
        points_3d = []

        for i in range(len(scores)):
            class_id = int(classes[i])
            confidence = scores[i]

            if class_id in self.target_classes:
                # ---------------------------------------------------
                # 💡 BÍ KÍP CẢI TIẾN: NGƯỠNG TỰ TIN KÉP (CLASS-SPECIFIC THRESHOLD)
                # ---------------------------------------------------
                min_conf = 0.40 # Mặc định
                if class_id == 0:  
                    min_conf = 0.45 # Người rất bự -> Đòi hỏi độ chắc chắn 45% (Chống ảo giác)
                # elif class_id == 39: 
                #     min_conf = 0.25 # Chai nước siêu nhỏ -> Ép AI phải nhạy cảm ở mức 25%
                elif class_id == 56: 
                    min_conf = 0.4 # Chai nước siêu nhỏ -> Ép AI phải nhạy cảm ở mức 25%

                # Nếu AI tự tin vượt qua ngưỡng riêng của vật thể đó
                if confidence > min_conf:
                    ymin, xmin, ymax, xmax = boxes[i]
                    x1, y1 = int(xmin * img_w), int(ymin * img_h)
                    x2, y2 = int(xmax * img_w), int(ymax * img_h)
                    
                    if y2 > self.horizon_y + 2.0:
                        Z = (self.fy * self.camera_height) / (y2 - self.horizon_y)
                        if 0.3 < Z <= 4.0:
                            valid_detection = True
                            object_name = self.target_classes[class_id]
                            current_valid_bboxes.append((x1, y1, x2, y2, Z, object_name))
                            
                            u_center = (x1 + x2) / 2.0
                            X = (u_center - self.cx) * Z / self.fx
                            H_width = (x2 - x1) * Z / self.fx 
                            
                            w_step = -H_width / 2.0
                            while w_step <= H_width / 2.0:
                                points_3d.append([Z, -(X + w_step), 0.2])
                                w_step += self.point_density

        # Lọc Debounce
        if valid_detection:
            self.consecutive_frames += 1
            if self.consecutive_frames > self.CONFIRM_THRESHOLD + 2:
                self.consecutive_frames = self.CONFIRM_THRESHOLD + 2
                
            if self.consecutive_frames >= self.CONFIRM_THRESHOLD:
                self.last_pc = points_3d
                self.last_bboxes = current_valid_bboxes
                self.publish_pointcloud(self.last_pc)
        else:
            if self.consecutive_frames > 0:
                self.consecutive_frames -= 1
            
            if self.consecutive_frames == 0:
                self.publish_pointcloud([])
                self.last_pc = []
                self.last_bboxes = []

        # Vẽ hình có kèm Tên Vật Thể
        # Vẽ hình có kèm Tên Vật Thể (ĐÃ BỎ IF ĐỂ ÉP HIỂN THỊ LUÔN)
        for (x1, y1, x2, y2, Z, obj_name) in self.last_bboxes:
            # Luôn vẽ khung xanh lá
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
            # Luôn in Text khoảng cách to, rõ ràng
            cv2.putText(frame, f"{obj_name}: {Z:.2f}m", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2) 

        success, encoded_image = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        if success:
            out_msg = CompressedImage()
            out_msg.header = msg.header
            out_msg.format = "jpeg"
            out_msg.data = encoded_image.tobytes()
            self.annotated_img_pub.publish(out_msg)
        
        # =========================================================
        # TÍNH TOÁN FPS (Khung hình/giây)
        # =========================================================
        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time) if (current_time - self.prev_time) > 0 else 0
        self.prev_time = current_time

        # =========================================================
        # VẼ GIAO DIỆN BẢNG ĐIỀU KHIỂN (HUD - HIỂN THỊ CALIB Y2)
        # =========================================================
        # 1. Tạo lớp nền đen mờ (Overlay) ở góc trái màn hình
        overlay = frame.copy()
        # Mở rộng chiều cao bảng đen và chiều ngang để chứa thêm thông số
        hud_height = 120 + len(self.last_bboxes) * 30 
        cv2.rectangle(overlay, (10, 10), (360, hud_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame) # Độ mờ 60%

        # 2. In thông số tổng quan hệ thống
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # ---> HIỂN THỊ THÔNG SỐ CALIB HIỆN TẠI (ĐỂ DỄ THEO DÕI) <---
        cv2.putText(frame, f"Calib: fy={self.fy:.1f}, Hy={self.horizon_y:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
        
        status_color = (0, 0, 255) if len(self.last_bboxes) > 0 else (0, 255, 0)
        status_text = "PHAT HIEN VAT CAN!" if len(self.last_bboxes) > 0 else "AN TOAN"
        cv2.putText(frame, f"Status: {status_text}", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        cv2.line(frame, (20, 95), (350, 95), (255, 255, 255), 1)

        # 3. Vẽ Bounding Box và liệt kê khoảng cách + y2 vào HUD
        y_hud_offset = 115
        for (x1, y1, x2, y2, Z, obj_name) in self.last_bboxes:
            # Vẽ khung xanh lá
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
            
            # In khoảng cách Z (m) ở trên đầu Bounding Box
            text_y = max(25, y1 - 10) 
            cv2.putText(frame, f"{Z:.2f}m", (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # ---> IN TỌA ĐỘ y2 NGAY TẠI GÓT CHÂN VẬT THỂ (Màu vàng) <---
            cv2.putText(frame, f"y2: {y2}", (x1, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            # Chấm 1 điểm tròn đỏ ngay giữa đáy khung
            cv2.circle(frame, (int((x1+x2)/2), y2), 5, (0, 0, 255), -1)

            # Ghi thông số vào Bảng điều khiển HUD (Kèm theo y2)
            cv2.putText(frame, f"- {obj_name}: {Z:.2f}m | y2: {y2}", (20, y_hud_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_hud_offset += 30

        # =========================================================
        # XUẤT ẢNH ĐÃ XỬ LÝ LÊN WEB VIEWER
        # =========================================================
        success, encoded_image = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        if success:
            out_msg = CompressedImage()
            out_msg.header = msg.header
            out_msg.format = "jpeg"
            out_msg.data = encoded_image.tobytes()
            self.annotated_img_pub.publish(out_msg)

    def publish_pointcloud(self, points):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'base_footprint' 
        pc2_msg = point_cloud2.create_cloud_xyz32(header, points)
        self.pc_pub.publish(pc2_msg)

def main(args=None):
    rclpy.init(args=args)
    node = AIFusionObstacleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()