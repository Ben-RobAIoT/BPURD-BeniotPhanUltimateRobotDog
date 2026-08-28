import cv2
import time
import psutil
import numpy as np
import os

# Thử import tflite, nếu lỗi thì dùng tensorflow.lite
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

def benchmark_mobilenet_headless():
    print("🚀 ĐANG KHỞI ĐỘNG BÀI TEST MOBILENET-SSD (TFLITE INT8) TRÊN PI 4...")
    
    # Đường dẫn tới model vừa tải
    model_path = "tflite_model/detect.tflite"
    if not os.path.exists(model_path):
        print("❌ Không tìm thấy model! Hãy chắc chắn bạn đã tải và giải nén đúng thư mục.")
        return

    # Load TFLite Model
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    # Mở Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Không thể mở Camera!")
        return

    fps_list = []
    cpu_list = []
    
    print("⏳ Đang đo đạc (100 khung hình)... Hãy di chuyển trước camera để AI nhận diện.")
    print("--------------------------------------------------")
    
    frames_processed = 0

    while frames_processed < 100:
        ret, frame = cap.read()
        if not ret: break

        start_infer = time.time()
        
        # Tiền xử lý ảnh (Resize về 300x300 cho MobileNet)
        frame_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # CHẠY SUY LUẬN AI (TFLITE)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        # Lấy kết quả (Chỉ lấy boxes và classes, không cần vẽ ra vì là headless)
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class ID
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence
        
        end_infer = time.time()
        
        # Tính toán
        infer_time = end_infer - start_infer
        fps = 1.0 / infer_time if infer_time > 0 else 0
        fps_list.append(fps)
        
        cpu_usage = psutil.cpu_percent(interval=None)
        cpu_list.append(cpu_usage)
        
        frames_processed += 1
        
        if frames_processed % 10 == 0:
            print(f"👉 Đã xử lý {frames_processed}/100 khung hình... (Tốc độ tức thời: {fps:.1f} FPS)")

    cap.release()

    # TỔNG KẾT BÁO CÁO
    avg_fps = sum(fps_list) / len(fps_list)
    avg_cpu = sum(cpu_list) / len(cpu_list)
    
    print("\n" + "="*45)
    print("📊 KẾT QUẢ BENCHMARK MOBILENET-SSD (TFLITE - PI 4)")
    print("="*45)
    print(f"⏱️ Tốc độ trung bình  : {avg_fps:.2f} FPS")
    print(f"🔥 Tải CPU AI ngốn    : {avg_cpu:.1f} %")
    print(f"⚠️ Đánh giá cho Nav2  : {'CẢNH BÁO NGUY HIỂM' if avg_cpu > 60 else 'AN TOÀN (Có thể chạy chung Nav2)'}")
    print("="*45)

if __name__ == '__main__':
    benchmark_mobilenet_headless()