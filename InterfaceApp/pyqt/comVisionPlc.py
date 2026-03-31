"""Vision PLC Communication - State Machine for PLC + YOLO"""
from enum import Enum, auto
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from collections import deque


class Step(Enum):
    WAIT_PLC = auto()
    VERIFY_OBJ = auto()
    SEND_DATA = auto()
    WAIT_COMPLETE = auto()


class VisionPlcHandler(QObject):
    """Xử lý chu trình Vision + PLC"""
    status = pyqtSignal(str)
    
    def __init__(self, plc, vision):
        super().__init__()
        self.plc = plc
        self.vision = vision
        self.step = Step.WAIT_PLC
        
        # Buffer lưu 10 frame detection
        self.detection_buffer = deque(maxlen=10)
        self.verified_object = None
        
        # Timer chạy chu trình
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)
        
    def start(self):
        """Bắt đầu chu trình"""
        self.step = Step.WAIT_PLC
        self.timer.start(50)  # 20Hz
        self.status.emit("Auto cycle started")
        
    def stop(self):
        """Dừng chu trình"""
        self.timer.stop()
        self.status.emit("Auto cycle stopped")
        
    def is_running(self):
        return self.timer.isActive()
        
    def run_cycle(self):
        """Chu trình chính - match case"""
        if not self.plc or not self.plc.is_connected():
            return
            
        match self.step:
            case Step.WAIT_PLC:
                self._step_wait_plc()
            case Step.VERIFY_OBJ:
                self._step_verify()
            case Step.SEND_DATA:
                self._step_send()
            case Step.WAIT_COMPLETE:
                self._step_wait_complete()
    
    def _step_wait_plc(self):
        """Step 1: Chờ PLC bit ON"""
        if self.plc.i_autoModeReady:
            self.status.emit("PLC ready, verifying object...")
            self.detection_buffer.clear()
            self.step = Step.VERIFY_OBJ
            
    def _step_verify(self):
        """Step 2: Kiểm tra 10 khung hình để xác nhận (cần 7/10 đúng)"""
        from collections import Counter
        
        dets = self.vision.get_detections()
        
        if dets:
            # Lấy vùng data trong yol0
            obj = dets[0]
            # Gán data vào buffer
            self.detection_buffer.append({
                'id': obj.get('id', 0),
                'class': obj.get('class', '?'),
                'x': obj.get('x', 0),
                'y': obj.get('y', 0)
            })
            
            # Đủ 10 mẫu, kiểm tra 7/10 giống nhau
            if len(self.detection_buffer) >= 10:
                # Cách ngắn gọn để lấy giá trị id duyệt qua detection_buffer
                ids = [d['id'] for d in self.detection_buffer]
                id_counts = Counter(ids)
                most_common_id, count = id_counts.most_common(1)[0]
                
                if count >= 7:  # 7/10 trở lên = hợp lệ
                    # Lấy object cuối cùng có ID phổ biến nhất - reversed() - cho chạy for ngược
                    for d in reversed(self.detection_buffer):
                        if d['id'] == most_common_id:
                            self.verified_object = d
                            break
                    c = self.verified_object['class']
                    x, y = self.verified_object['x'], self.verified_object['y']
                    self.status.emit(f"Verified {c} at ({x},{y}) ({count}/10)")
                    self.detection_buffer.clear()
                    self.step = Step.SEND_DATA
                else:
                    # Không đủ 7/10, loại bỏ mẫu cũ nhất (sliding window)
                    self.detection_buffer.popleft()
        else:
            # Không detect được, quay lại đợi PLC
            self.status.emit("No object detected")
            self.detection_buffer.clear()
            self.step = Step.WAIT_PLC
            
    def _step_send(self):
        """Step 3: Gửi dữ liệu sang PLC"""
        # Ghi vào thanh ghi PLC
        self.plc.o_visionObjectX = self.verified_object['x']
        self.plc.o_visionObjectY = self.verified_object['y']
        self.plc.o_visionObjectType = self.verified_object['id']
        self.plc.o_visionEncoder = self.plc.i_CurrentEncoder
        self.plc.o_visionReady = 1
        
        # Gọi lệnh write_data của PLC
        
        c = self.verified_object['class']
        x, y = self.verified_object['x'], self.verified_object['y']
        self.status.emit(f"Sent {c}: X={x} Y={y}")
        self.step = Step.WAIT_COMPLETE
        
    def _step_wait_complete(self):
        """Step 4: Chờ PLC xử lý xong (bit OFF), về step 1"""
        if not self.plc.i_autoModeReady:
            self.verified_object = None
            self.detection_buffer.clear()
            self.status.emit("Cycle complete, waiting...")
            self.step = Step.WAIT_PLC
            
    def get_current_step(self):
        return self.step.name
