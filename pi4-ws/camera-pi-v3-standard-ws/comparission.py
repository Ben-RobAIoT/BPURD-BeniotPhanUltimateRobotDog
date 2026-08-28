import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Dữ liệu bạn vừa test được
models = ['YOLOv8n (ONNX)', 'MobileNet-SSD (TFLite)']
fps = [1.78, 7.72]       # Tốc độ (Cao hơn là tốt hơn)
cpu = [99.3, 26.2]       # % CPU (Thấp hơn là tốt hơn)

x = np.arange(len(models))
width = 0.35

fig, ax1 = plt.subplots(figsize=(10, 6))

# Vẽ cột FPS (Trục trái)
rects1 = ax1.bar(x - width/2, fps, width, label='Tốc độ (FPS)', color='#4CAF50', edgecolor='black')
ax1.set_ylabel('Tốc độ xử lý (Frames per Second)', color='#1b5e20', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#1b5e20')
ax1.set_ylim(0, 10)

# Tạo trục phải cho CPU
ax2 = ax1.twinx()
rects2 = ax2.bar(x + width/2, cpu, width, label='Mức ngốn CPU (%)', color='#F44336', edgecolor='black')
ax2.set_ylabel('Tài nguyên CPU (%)', color='#b71c1c', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#b71c1c')
ax2.set_ylim(0, 110)

# Trang trí
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=12, fontweight='bold')
plt.title('ĐÁNH GIÁ ĐỐI CHỨNG THUẬT TOÁN AI TRÊN RASPBERRY PI 4\n(Tiêu chí Hiệu năng tính toán)', fontsize=14, fontweight='bold', pad=20)

# Hiển thị số trên cột
def autolabel(rects, ax, suffix=""):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}{suffix}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

autolabel(rects1, ax1, " fps")
autolabel(rects2, ax2, "%")

# Chú thích
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.85), bbox_transform=ax1.transAxes)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.savefig("AI_Performance_Comparison.png", dpi=300, bbox_inches='tight')
print("✅ Đã xuất biểu đồ so sánh ra file AI_Performance_Comparison.png")