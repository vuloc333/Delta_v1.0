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
        """Detect toàn frame, chỉ giữ vật NGOÀI ROI, loại BlueTri, chọn vật gần gốc tọa độ nhất"""
        if frame is None or self.model is None:
            return frame, []
        
        # ROI bounds
        rx1 = min(self.roi_x, frame.shape[1])
        ry1 = min(self.roi_y, frame.shape[0])
        rx2 = min(self.roi_x + self.roi_w, frame.shape[1])
        ry2 = min(self.roi_y + self.roi_h, frame.shape[0])
        
        # YOLO detect trên toàn frame
        results = self.model.predict(frame, verbose=False, iou=0.2, conf=0.35)
        
        all_detections = []
        for r in results:
            for box in r.boxes:
                x, y, bw, bh = box.xywh[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                x, y = int(x), int(y)
                
                # Mapping class ID: 0=BlueTri (loại), 1=RedRec→2, 2=YelCir→1
                id_map = {0: None, 1 : 1, 2 : 2}
                mapped_id = id_map.get(cls)
                if mapped_id is None:
                    continue
                    
                # Chỉ giữ vật TRONG ROI
                in_roi = (rx1 <= x <= rx2) and (ry1 <= y <= ry2)
                if not in_roi:
                    continue
                
                name = r.names.get(cls, str(cls))
                all_detections.append({
                    'id': mapped_id, 'class': name, 'x': x, 'y': y, 
                    'w': int(bw), 'h': int(bh), 'confidence': conf
                })
        
        # Vẽ ROI border (màu đỏ)
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)
        cv2.putText(frame, "ROI", (rx1, ry1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Chọn vật có tọa độ nhỏ nhất (x+y nhỏ nhất)
        if all_detections:
            best = min(all_detections, key=lambda d: d['x'] + d['y'])
            # Chỉ vẽ vật được chọn
            bw, bh = best['w'], best['h']
            x1b, y1b = int(best['x'] - bw/2), int(best['y'] - bh/2)
            x2b, y2b = int(best['x'] + bw/2), int(best['y'] + bh/2)
            cv2.rectangle(frame, (x1b, y1b), (x2b, y2b), (0, 255, 0), 2)
            cv2.putText(frame, f"{best['class']} {best['confidence']:.2f}", (x1b, y1b-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            return frame, [best]
        
        return frame, []
        
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
