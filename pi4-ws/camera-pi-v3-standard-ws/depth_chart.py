import matplotlib.pyplot as plt
import numpy as np

# 1. NHẬP SỐ LIỆU BẠN ĐO ĐƯỢC VÀO ĐÂY
true_dist = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
# Sửa các số bên dưới thành số bạn nhìn thấy trên màn hình Web Viewer
ai_est_dist = np.array([1.03, 1.56, 2.12, 2.68, 3.25]) 

# Tính toán sai số
error = np.abs(ai_est_dist - true_dist) * 100 # Đổi ra cm

# 2. CẤU HÌNH VẼ BIỂU ĐỒ CHUẨN KHOA HỌC
plt.figure(figsize=(10, 6))

# Đường lý tưởng (Ground Truth)
plt.plot(true_dist, true_dist, color='black', linestyle='--', linewidth=2, label='Đường lý tưởng (Sai số = 0)')

# Đường AI nội suy được
plt.plot(true_dist, ai_est_dist, color='blue', marker='o', markersize=8, linewidth=2, label='Kết quả AI nội suy (Pseudo-Depth)')

# Tô màu vùng sai số
plt.fill_between(true_dist, true_dist, ai_est_dist, color='red', alpha=0.15, label='Vùng sai số')

# 3. TRANG TRÍ BIỂU ĐỒ
for i, txt in enumerate(error):
    plt.annotate(f"Lệch {txt:.1f}cm", (true_dist[i], ai_est_dist[i]), textcoords="offset points", xytext=(0,10), ha='center', color='red', fontweight='bold')

plt.title('ĐÁNH GIÁ SAI SỐ THUẬT TOÁN ƯỚC LƯỢNG KHOẢNG CÁCH MONOCULAR PSEUDO-DEPTH', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Khoảng cách thực tế đo bằng thước (mét)', fontsize=12)
plt.ylabel('Khoảng cách hệ thống AI tính toán (mét)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper left', fontsize=11)
plt.xlim(0.8, 3.2)
plt.ylim(0.8, 3.5)

# Lưu hình ảnh chất lượng cao để chèn vào Word
plt.savefig('depth_chart.png', dpi=300, bbox_inches='tight')
print("Đã lưu biểu đồ thành công vào file 'depth_chart.png'!")
plt.show()