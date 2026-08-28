import subprocess
import cv2
import numpy as np
from flask import Flask, Response
from ultralytics import YOLO

app = Flask(__name__)

# Nạp bộ não AI siêu nhẹ (ONNX)
print("Đang nạp não AI YOLOv8n (ONNX)... Vui lòng đợi vài giây...")
model = YOLO('yolov8n.onnx', task='detect')
print("Nạp não thành công! Sẵn sàng chiến đấu.")

# Hàm đếm byte chuẩn xác 100% để chống rách hình
def read_exactly(pipe, size):
    data = b''
    while len(data) < size:
        chunk = pipe.read(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def generate_frames():
    # Giảm xuống 10fps để CPU Pi 3 kịp xử lý AI mà không bị quá tải
    # GStreamer có lắp VAN XẢ ÁP SUẤT (queue leaky) để chống kẹt CPU
    cmd = [
        "gst-launch-1.0", "-q",
        "libcamerasrc", "!",
        "video/x-raw,width=640,height=480,framerate=10/1", "!",
        "videoconvert", "!",
        "video/x-raw,format=RGB", "!",
        "queue", "max-size-buffers=1", "leaky=downstream", "!", 
        "fdsink", "fd=1"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frame_size = 640 * 480 * 3 

    try:
        while True:
            raw_data = read_exactly(process.stdout, frame_size)
            if not raw_data:
                print("Luồng camera bị ngắt.")
                break

            frame = np.frombuffer(raw_data, dtype=np.uint8).reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # ==========================================
            # KHU VỰC NÃO AI HOẠT ĐỘNG
            # classes=[0]: Tui ra lệnh cho nó CHỈ tìm Người (Person), bỏ qua chó mèo xe cộ
            # conf=0.4: Độ tự tin phải trên 40% mới đánh dấu, chống nhận diện bậy bạ
            # ==========================================
            results = model.predict(frame_bgr, classes=[0], conf=0.4, verbose=False)
            
            # Hàm plot() sẽ tự động vẽ cái khung màu đỏ bao quanh người
            annotated_frame = results[0].plot()

            # Nén bức ảnh đã có khung nhận diện thành JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        process.terminate()

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)