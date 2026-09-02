import mediapipe as mp
import cv2

class GestureDictionary:
    def __init__(self):
        # Khởi tạo MediaPipe 1 lần duy nhất để tiết kiệm RAM
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def process_and_recognize(self, img_bgr):
        """
        Nhận ảnh BGR từ camera, vẽ khung xương và trả về Lệnh điều khiển.
        """
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        command = "NONE"
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 1. Gọi hàm đối chiếu từ điển để lấy lệnh
                command = self._check_dictionary(hand_landmarks)
                
                # 2. Vẽ khung xương lên ảnh
                self.mp_draw.draw_landmarks(
                    img_bgr, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )
                
        return command, img_bgr

    def _check_dictionary(self, hand_landmarks):
        """
        NƠI LƯU TRỮ CÁC KÝ HIỆU TAY.
        Sau này muốn thêm bớt cử chỉ, cậu CHỈ CẦN SỬA Ở ĐÂY.
        """
        # Lấy tọa độ Y của các ngón quan trọng (0 là cổ tay, 8 là ngón trỏ, 12 là ngón giữa)
        y_wrist = hand_landmarks.landmark[0].y
        y_index_tip = hand_landmarks.landmark[8].y
        y_mid_tip = hand_landmarks.landmark[12].y
        
        # --- KÝ HIỆU 1: "STOP" (Xòe tay, ngón giữa cao hơn cổ tay nhiều) ---
        if y_mid_tip < y_wrist - 0.2:
            return "STOP"
            
        # --- (Dành cho sau này) KÝ HIỆU 2: "BACKWARD" (Ví dụ: Ngón trỏ chỉ xuống) ---
        # elif y_index_tip > y_wrist + 0.1:
        #     return "BACKWARD"
            
        # --- MẶC ĐỊNH: Không khớp ký hiệu nào thì cho đi tới ---
        else:
            return "FORWARD"