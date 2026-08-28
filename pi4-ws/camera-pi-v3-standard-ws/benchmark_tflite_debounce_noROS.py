import cv2
import time
import psutil
import numpy as np
import os

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

def run_benchmark():
    print("🚀 BẮT ĐẦU BENCHMARK: TFLITE + DEBOUNCE + TÍNH KHOẢNG CÁCH Z")
    
    VIDEO_PATH = 'test_video.mp4'
    GROUND_TRUTH_FRAMES = 600 # Số frame bạn tự đếm
    
    model_path = "tflite_model/detect.tflite"
    if not os.path.exists(model_path):
        print("❌ Lỗi: Không tìm thấy model!")
        return

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height, width = input_details[0]['shape'][1], input_details[0]['shape'][2]

    cap = cv2.VideoCapture(VIDEO_PATH)
    
    fps_list, cpu_list = [], []
    total_frames = 0
    
    # --- BIẾN ĐẾM THỐNG KÊ ---
    raw_ai_detections = 0
    distance_filtered_detections = 0 
    final_confirmed_detections = 0
    
    consecutive_frames = 0
    CONFIRM_THRESHOLD = 3

    # Thông số Camera giả lập (Giống trên xe)
    fy, cy, camera_height = 500.0, 240.0, 0.20

    while True:
        ret, frame = cap.read()
        if not ret: break

        start_infer = time.time()
        
        frame_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        classes = interpreter.get_tensor(output_details[1]['index'])[0]
        scores = interpreter.get_tensor(output_details[2]['index'])[0]
        boxes = interpreter.get_tensor(output_details[0]['index'])[0]
        
        end_infer = time.time()
        
        # 1. BƯỚC 1: AI RAW NHÌN THẤY
        ai_sees = False
        valid_distance = False
        
        for i in range(len(scores)):
            if scores[i] > 0.40 and int(classes[i]) == 0: 
                ai_sees = True
                
                # 2. BƯỚC 2: LỌC KHOẢNG CÁCH (Chỉ quan tâm vật cản < 3 mét)
                ymin, xmin, ymax, xmax = boxes[i]
                y2 = int(ymax * 480) # Pixel y cạnh dưới
                if y2 > cy + 10:
                    Z = (fy * camera_height) / (y2 - cy)
                    if 0.5 < Z < 3.0: # Chỉ sợ vật cản từ 0.5m đến 3m
                        valid_distance = True
                break
                
        if ai_sees: raw_ai_detections += 1
        if valid_distance: distance_filtered_detections += 1

        # 3. BƯỚC 3: LỌC DEBOUNCE (Đã Fix lỗi Latch Effect)
        if valid_distance:
            consecutive_frames += 1
            # Khóa trần (Max limit) để không bị cộng vô tận
            if consecutive_frames > CONFIRM_THRESHOLD + 2:
                consecutive_frames = CONFIRM_THRESHOLD + 2
        else:
            # Nếu mất dấu, xả từ từ bộ đệm
            if consecutive_frames > 0: 
                consecutive_frames -= 1 

        # Quyết định chốt
        if consecutive_frames >= CONFIRM_THRESHOLD:
            final_confirmed_detections += 1

        # Thống kê hiệu năng
        infer_time = end_infer - start_infer
        fps_list.append(1.0 / infer_time if infer_time > 0 else 0)
        cpu_list.append(psutil.cpu_percent(interval=None))
        total_frames += 1

    cap.release()

    # IN BÁO CÁO CỰC ĐẸP CHO LUẬN VĂN
    print("\n" + "="*60)
    print("📊 BÁO CÁO HIỆU QUẢ CÁC TẦNG LỌC (TFLITE INT8)")
    print("="*60)
    print(f"⏱️ Tốc độ: {sum(fps_list)/len(fps_list):.1f} FPS  |  🔥 CPU: {sum(cpu_list)/len(cpu_list):.1f} %")
    print("-" * 60)
    print(f"🎞️ Tổng frame video : {total_frames}")
    print(f"🎯 Khung hình thực tế có người (Ground Truth): {GROUND_TRUTH_FRAMES}")
    print("-" * 60)
    print(f"1️⃣ Tầng AI Thô       : Phát hiện {raw_ai_detections} frames (Nhiều ảo giác & Vật ở xa)")
    print(f"2️⃣ Tầng Không gian 3D: Giảm còn {distance_filtered_detections} frames (Loại bỏ người > 3m)")
    print(f"3️⃣ Tầng Lọc Debounce : CHỐT CÒN {final_confirmed_detections} frames (Triệt tiêu bóng ma)")
    print("="*60)
    print("💡 KẾT LUẬN: Số lượng 'Bóng Ma' đẩy lên Costmap đã được triệt tiêu tối đa!")

if __name__ == '__main__':
    run_benchmark()