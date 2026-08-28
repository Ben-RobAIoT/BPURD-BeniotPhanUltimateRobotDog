import cv2
import time
import psutil
from ultralytics import YOLO

def benchmark_yolov8_video():
    print("🚀 ĐANG TEST YOLOv8n (ONNX) TRÊN VIDEO...")
    
    # THÔNG SỐ BẠN CẦN CHỈNH SỬA (Giống hệt bên kia để công bằng)
    VIDEO_PATH = 'test_video.mp4'
    GROUND_TRUTH_FRAMES = 600  
                                                                  
    try:
        model = YOLO('yolov8n.onnx', task='detect')
    except Exception as e:
        print(f"❌ Lỗi load model: {e}")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Không thể mở video: {VIDEO_PATH}")
        return

    fps_list, cpu_list = [], []
    total_frames = 0
    detected_frames = 0

    print(f"⏳ Đang xử lý video... (Sẽ hơi lâu vì CPU 100%)")
    
    while True:
        ret, frame = cap.read()
        if not ret: break

        start_infer = time.time()
        
        # CHẠY SUY LUẬN AI (Chỉ tìm class 0: người)
        results = model.predict(frame, classes=[0], conf=0.35, imgsz=640, verbose=False)
        
        end_infer = time.time()
        
        # ĐẾM ĐỘ CHÍNH XÁC: Xem box có rỗng không?
        person_found = False
        for result in results:
            if len(result.boxes) > 0:
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

    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    avg_cpu = sum(cpu_list) / len(cpu_list) if cpu_list else 0
    accuracy = (detected_frames / GROUND_TRUTH_FRAMES) * 100 if GROUND_TRUTH_FRAMES > 0 else 0
    false_negatives = GROUND_TRUTH_FRAMES - detected_frames

    print("\n" + "="*50)
    print("📊 KẾT QUẢ BENCHMARK YOLOv8n (VIDEO TEST)")
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
    benchmark_yolov8_video()