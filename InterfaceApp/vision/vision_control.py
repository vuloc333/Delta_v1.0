"""Vision Control - Simple YOLO detection for PyQt"""
import cv2
import os
import time
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from ultralytics import YOLO

# Chặn warning MSMF từ OpenCV
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'


class VisionProcessor(QThread):
    """Thread xử lý camera và YOLO"""
    frame_ready = pyqtSignal(object, list)  # frame(numpy), detections
    
    def __init__(self, camera_id=1):
        super().__init__()
        self.camera_id = camera_id
        self.running = False
        self.cap = None
        self.model = None
        
        # ROI settings
        self.roi_x = 0
        self.roi_y = 0
        self.roi_w = 640
        self.roi_h = 480
        
        # Detection results
        self.detections = []
        self.frame_width = 640
        self.frame_height = 480
        
    def load_model(self):
        """Load YOLO model - tự động chọn device"""
        try:
            # Absolute path để tránh lỗi khi chạy từ folder khác
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "runs", "detect", "train2", "weights", "best.pt")
            self.model = YOLO(model_path)
            print(f"YOLO loaded: {model_path}")
            return True
        except Exception as e:
            print(f"Model error: {e}")
            return False
    
    def init_camera(self):
        """Mở camera - dùng DSHOW backend (ổn định hơn MSMF)"""
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if self.cap.isOpened():
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Camera: {self.frame_width}x{self.frame_height}")
            return True
        return False
    
    def restart_camera(self):
        """Khởi động lại camera khi gặp lỗi"""
        print("Restarting camera...")
        if self.cap:
            self.cap.release()
        time.sleep(0.5)
        return self.init_camera()
    
    def set_roi(self, x, y, w, h):
        """Set ROI region"""
        self.roi_x = max(0, x)
        self.roi_y = max(0, y)
        self.roi_w = max(1, w)
        self.roi_h = max(1, h)
        
    def detect(self, frame):
        """Detect vật thể trong ROI, trả về frame đã vẽ và danh sách detection"""
        # Tính ROI trong frame
        x1 = min(self.roi_x, frame.shape[1])
        y1 = min(self.roi_y, frame.shape[0])
        x2 = min(self.roi_x + self.roi_w, frame.shape[1])
        y2 = min(self.roi_y + self.roi_h, frame.shape[0])
        
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0 or self.model is None:
            return frame, []
        
        # YOLO detect
        results = self.model.predict(roi, verbose=False, iou=0.2, conf=0.35)
        
        detections = []
        for r in results:
            for box in r.boxes:
                x, y, bw, bh = box.xywh[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Tọa độ toàn cục
                abs_x = int(x) + x1
                abs_y = int(y) + y1
                name = r.names.get(cls, str(cls))
                
                detections.append({
                    'id': cls, 'class': name, 'x': abs_x, 'y': abs_y, 'confidence': conf
                })
                
                # Vẽ box
                x1b, y1b = int(abs_x - bw/2), int(abs_y - bh/2)
                x2b, y2b = int(abs_x + bw/2), int(abs_y + bh/2)
                cv2.rectangle(frame, (x1b, y1b), (x2b, y2b), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} {conf:.2f}", (x1b, y1b-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Vẽ ROI border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        return frame, detections
        
    def run(self):
        if not self.load_model() or not self.init_camera():
            return
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                annotated, dets = self.detect(frame)
                self.detections = dets
                self.frame_ready.emit(annotated, dets)
            else:
                self.restart_camera()
            self.msleep(33)
        self.cap.release()
    
    def stop(self):
        self.running = False
        self.wait()
        
    def get_detections(self):
        """Get latest detections, loại bỏ object id 0"""
        return [d for d in self.detections if d.get('id', 0) != 0]
        
    def get_frame_size(self):
        """Get camera frame size"""
        return self.frame_width, self.frame_height


class VisionControl:
    """API cho UI - đơn giản, chỉ chuyển tiếp"""
    def __init__(self, label, camera_id=1):
        self.label = label
        self.thread = VisionProcessor(camera_id)
        self.thread.frame_ready.connect(self._update_ui)
        
    def _update_ui(self, frame, detections):
        """Cập nhật QLabel với frame mới"""
        try:
            if frame is None or self.label is None:
                return
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(img)
            scaled = pix.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.label.setPixmap(scaled)
        except:
            pass
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.thread.stop()
    
    def set_roi(self, x, y, w, h):
        self.thread.set_roi(x, y, w, h)
    
    def get_detections(self):
        """Get latest detections, loại bỏ object id 0"""
        return self.thread.get_detections()
    
    def get_frame_size(self):
        return self.thread.frame_width, self.thread.frame_height
    
    def is_ready(self):
        return self.thread.cap is not None and self.thread.cap.isOpened()
