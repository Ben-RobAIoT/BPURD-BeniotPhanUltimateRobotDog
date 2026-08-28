import cv2
import time
import psutil
import numpy as np
import os

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

def benchmark_mobilenet_video():
    print("🚀 ĐANG TEST MOBILENET-SSD (TFLITE) TRÊN VIDEO...")
    
    # THÔNG SỐ BẠN CẦN CHỈNH SỬA
    VIDEO_PATH = 'test_video.mp4'
    """
    
    """
    GROUND_TRUTH_FRAMES = 600  # Số khung hình THỰC TẾ có người (bạn tự đếm)
    
    model_path = "tflite_model/detect.tflite"
    if not os.path.exists(model_path):
        print("❌ Lỗi: Không tìm thấy file model detect.tflite")
        return

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Không thể mở video: {VIDEO_PATH}")
        return

    fps_list, cpu_list = [], []
    total_frames = 0
    detected_frames = 0 # Bộ đếm số frame phát hiện được người

    print(f"⏳ Đang xử lý video... (Sẽ chạy cho đến khi hết video)")
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            break # Hết video

        start_infer = time.time()
        
        # Tiền xử lý
        frame_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Chạy AI
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        classes = interpreter.get_tensor(output_details[1]['index'])[0]
        scores = interpreter.get_tensor(output_details[2]['index'])[0]
        
        end_infer = time.time()
        
        # KIỂM TRA ĐỘ CHÍNH XÁC: Có người (class 0) và tự tin > 35% không?
        person_found = False
        for i in range(len(scores)):
            # Trong model COCO của TFLite, class 0 thường là person
            if scores[i] > 0.35 and classes[i] == 0: 
                person_found = True
                break
                
        if person_found:
            detected_frames += 1

        # Ghi nhận hiệu năng
        infer_time = end_infer - start_infer
        fps_list.append(1.0 / infer_time if infer_time > 0 else 0)
        cpu_list.append(psutil.cpu_percent(interval=None))
        total_frames += 1
        
        if total_frames % 20 == 0:
            print(f"👉 Đã xử lý {total_frames} frame...")

    cap.release()

    # TÍNH TOÁN KẾT QUẢ ĐỐI CHỨNG
    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    avg_cpu = sum(cpu_list) / len(cpu_list) if cpu_list else 0
    
    accuracy = (detected_frames / GROUND_TRUTH_FRAMES) * 100 if GROUND_TRUTH_FRAMES > 0 else 0
    false_negatives = GROUND_TRUTH_FRAMES - detected_frames

    print("\n" + "="*50)
    print("📊 KẾT QUẢ BENCHMARK MOBILENET-SSD (VIDEO TEST)")
    print("="*50)
    print(f"🎞️ Tổng số frame đã xử lý  : {total_frames}")
    print(f"⏱️ Tốc độ trung bình (FPS) : {avg_fps:.2f}")
    print(f"🔥 Tải CPU ngốn            : {avg_cpu:.1f} %")
    print("-" * 50)
    print(f"🎯 Nhận diện đúng (True)   : {detected_frames} / {GROUND_TRUTH_FRAMES} frames")
    print(f"❌ Bỏ sót (False Negative) : {false_negatives} frames")
    print(f"🏆 ĐỘ NHẠY (ACCURACY)      : {accuracy:.1f} %")
    print("="*50)

if __name__ == '__main__':
    benchmark_mobilenet_video()