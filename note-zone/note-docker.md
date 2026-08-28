Chào bạn! Việc chuyển đổi từ tư duy thiết lập môi trường thủ công sang container hóa là một bước tiến lớn cho các dự án kỹ thuật phần mềm. Dưới đây là cách tiếp cận Docker được cấu trúc theo **phương pháp ghi chép Cornell**, giúp bạn hệ thống hóa các khái niệm cốt lõi và tư duy làm việc.

Trước khi đi vào chi tiết bảng ghi chép, hãy nhìn lướt qua cách các thành phần trong Docker tương tác với nhau:

> **Lưu ý ở hình trên:** Bạn sẽ thấy quy trình làm việc luôn đi theo một chiều chuẩn mực: Định nghĩa bằng file text (`Dockerfile`) ➔ Đóng gói thành bản mẫu (`Image`) ➔ Chạy thực tế (`Container`). Bạn cũng có thể lưu trữ và tải các bản mẫu này từ một kho lưu trữ đám mây (`Registry`).

---

## Bảng Ghi Chép Cornell: Tư Duy Làm Việc Với Docker

| Từ khóa / Câu hỏi (Cues) | Ghi chép chi tiết (Notes) |
| --- | --- |
| **Docker là gì? Khác gì với môi trường ảo thông thường?** | • **Khái niệm:** Một nền tảng để "đóng gói" toàn bộ ứng dụng (code, thư viện, biến môi trường, hệ điều hành thu nhỏ) vào một khối duy nhất.<br>

<br>• **Sự khác biệt:** Nếu bạn dùng `venv` cho Python, nó chỉ cách ly các thư viện (dependencies). Docker tiến xa hơn: nó cách ly *cả hệ điều hành*. Ứng dụng của bạn sẽ chạy y hệt nhau trên máy tính cá nhân, trên GitHub Actions, hay trên máy chủ thật mà không bao giờ gặp lỗi "nhưng nó chạy ngon trên máy tui!". |
| **Image vs. Container** | • **Docker Image (Khuôn đúc / Bản thiết kế):** Là một gói tĩnh, không thay đổi (read-only). Chứa mã nguồn và môi trường. Giống như bản snapshot của ứng dụng tại một thời điểm.<br>

<br>• **Docker Container (Thực thể sống):** Là một *Image đang được chạy*. Bạn có thể chạy nhiều Container độc lập từ cùng một Image duy nhất. Dữ liệu tạo ra trong quá trình Container chạy sẽ bị mất khi Container bị xóa (trừ khi bạn gắn ổ cứng ảo - Volume). |
| **Dockerfile là gì?** | • Là một file kịch bản (script) hướng dẫn Docker cách tạo ra một **Image**.<br>

<br>• **Ví dụ thực tế:** Thay vì bạn tự gõ lệnh, Dockerfile sẽ ghi lại các bước: Kéo hệ điều hành cơ sở (VD: `python:3.11-slim`) ➔ Copy mã nguồn vào ➔ Chạy `pip install -r requirements.txt` ➔ Định nghĩa lệnh khởi chạy ứng dụng. |
| **Docker Compose giải quyết bài toán gì?** | • Là công cụ quản lý nhiều Container chạy cùng lúc thông qua file `docker-compose.yml`.<br>

<br>• **Tư duy ứng dụng:** Khi dự án của bạn lớn lên, nó không chỉ có code Python. Bạn có thể cần một Container cho Backend, và một Container giả lập PostgreSQL (giống hệt Supabase) chạy song song ở local. Thay vì gõ nhiều lệnh rời rạc, bạn chỉ cần một lệnh `docker-compose up` là toàn bộ hệ thống sẽ được bật lên và tự động kết nối với nhau. |
| **Mindset / Vòng đời phát triển (Workflow)** | 1. **Code:** Viết mã nguồn như bình thường trên máy.<br>

<br>2. **Build:** Dùng `Dockerfile` để đóng gói mọi thứ thành **Image**.<br>

<br>3. **Test:** Chạy Image đó thành **Container** dưới local để kiểm tra.<br>

<br>4. **Ship & Deploy:** Đẩy Image lên Registry (như Docker Hub, GitHub Packages), sau đó máy chủ (Cloud/VPS) chỉ việc kéo Image đó về và chạy. |

---

## Trực quan hóa vòng đời của ứng dụng

Sơ đồ dưới đây minh họa sự thay đổi trạng thái của mã nguồn từ lúc phát triển đến lúc được khởi chạy và phân phối.

---

### Phần Tổng Kết (Summary)

**Cốt lõi của việc học Docker:** Docker thay đổi tư duy làm việc từ "cài đặt và cấu hình môi trường lặp đi lặp lại trên từng máy" sang "đóng gói môi trường kèm theo mã nguồn một lần duy nhất". Nắm vững ba khái niệm trụ cột: **Dockerfile** (Kịch bản) ➔ **Image** (Khuôn đúc tĩnh) ➔ **Container** (Tiến trình đang chạy). Khi thành thạo, bạn có thể dễ dàng mô phỏng và deploy những hệ thống phức tạp (gồm nhiều dịch vụ backend, database) chỉ bằng một vài dòng lệnh.
