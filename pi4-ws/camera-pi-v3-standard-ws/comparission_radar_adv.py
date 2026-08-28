import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# --- THÔNG SỐ ĐÃ CHUẨN HÓA (Thang điểm 100) ---
labels = ['Tốc độ khung hình (FPS)', 'Tiết kiệm CPU', 'Độ tin cậy\n(Ít nhận diện nhầm)', 'Độ nhẹ Model']

# Dữ liệu thực tế từ Video Benchmark của FDAMR
yolo_scores = [18, 0, 65, 60] 
mobilenet_scores = [77, 72, 38, 85]

# Xử lý tọa độ để vẽ Radar
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
yolo_scores += yolo_scores[:1]
mobilenet_scores += mobilenet_scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

# Tùy chỉnh background cho xịn xò
ax.set_facecolor('#f8f9fa')
ax.grid(color='#ced4da', linestyle='--', linewidth=1.5)

# Vẽ YOLOv8n
ax.plot(angles, yolo_scores, color='#E53935', linewidth=3, linestyle='-', label='YOLOv8n (ONNX)\nHiệu năng thấp, Độ tin cậy khá')
ax.fill(angles, yolo_scores, color='#E53935', alpha=0.15)
# Điểm nhấn YOLO
ax.scatter(angles, yolo_scores, color='#E53935', s=80, zorder=10)

# Vẽ MobileNet-SSD
ax.plot(angles, mobilenet_scores, color='#43A047', linewidth=3, linestyle='-', label='MobileNet-SSD (TFLite)\nHiệu năng cao, Dễ nhận diện nhầm')
ax.fill(angles, mobilenet_scores, color='#43A047', alpha=0.25)
# Điểm nhấn MobileNet
ax.scatter(angles, mobilenet_scores, color='#43A047', s=80, zorder=10)

# Căn chỉnh nhãn (Labels)
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=13, fontweight='bold', color='#343a40')

# Tiêu đề và Chú thích
plt.title('ĐÁNH GIÁ ĐA CHIỀU (TRADE-OFF) CÁC MÔ HÌNH AI\nTRÊN VI XỬ LÝ ARM RASPBERRY PI 4', size=16, fontweight='black', pad=30, color='#1e88e5')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), fontsize=11, ncol=2, frameon=True, shadow=True)

# Lưu ảnh
plt.savefig("AI_Radar_RealData.png", dpi=300, bbox_inches='tight')
print("✅ Đã xuất biểu đồ Radar từ dữ liệu thực tế: AI_Radar_RealData.png")