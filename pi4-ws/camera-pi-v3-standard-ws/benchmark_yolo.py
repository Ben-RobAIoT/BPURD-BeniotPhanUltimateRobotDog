import cv2
import time
import psutil
from ultralytics import YOLO

def benchmark_yolov8_headless():
    print("🚀 ĐANG KHỞI ĐỘNG BÀI TEST YOLOv8n (CHẾ ĐỘ HEADLESS - KHÔNG CẦN MÀN HÌNH)...")
    
    # Load model
    try:
        model = YOLO('yolov8n.onnx', task='detect')
    except Exception as e:
        print(f"Lỗi load model: {e}")
        return

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
        
        # CHẠY SUY LUẬN AI
        results = model.predict(frame, classes=[0], conf=0.35, imgsz=640, verbose=False)
        
        end_infer = time.time()
        
        # Tính toán
        infer_time = end_infer - start_infer
        fps = 1.0 / infer_time if infer_time > 0 else 0
        fps_list.append(fps)
        
        cpu_usage = psutil.cpu_percent(interval=None)
        cpu_list.append(cpu_usage)
        
        frames_processed += 1
        
        # Cập nhật tiến độ mỗi 10 frame để bạn không tưởng máy bị treo
        if frames_processed % 10 == 0:
            print(f"👉 Đã xử lý {frames_processed}/100 khung hình... (Tốc độ tức thời: {fps:.1f} FPS)")

    cap.release()

    # TỔNG KẾT BÁO CÁO
    avg_fps = sum(fps_list) / len(fps_list)
    avg_cpu = sum(cpu_list) / len(cpu_list)
    
    print("\n" + "="*45)
    print("📊 KẾT QUẢ BENCHMARK YOLOV8N (NATIVE CPU PI 4)")
    print("="*45)
    print(f"⏱️ Tốc độ trung bình  : {avg_fps:.2f} FPS")
    print(f"🔥 Tải CPU AI ngốn    : {avg_cpu:.1f} %")
    print(f"⚠️ Đánh giá cho Nav2  : {'CẢNH BÁO NGUY HIỂM (CPU quá tải)' if avg_cpu > 50 else 'TẠM ỔN (Có thể chạy chung Nav2)'}")
    print("="*45)

if __name__ == '__main__':
    benchmark_yolov8_headless()