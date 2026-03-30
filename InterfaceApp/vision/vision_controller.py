import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import onnxruntime as ort

class VisionThread(QThread):
    """ONNX inference runs in separate thread to avoid DLL conflict with PyQt"""
    pixmap_ready = pyqtSignal(QPixmap, list)  # (pixmap, detections)
    
    def __init__(self, camera_id=1, model_path=r"vision\runs\detect\train2\weights\best.onnx"):
        super().__init__()
        self.camera_id = camera_id
        self.model_path = model_path
        self.running = False
        self.session = None
        self.input_name = None
        self.class_names = ['BlueTri', 'RedRec', 'YelCir']
        self.cap = None
        
    def init_onnx(self):
        """Initialize ONNX with RX 470 DirectML - auto export if needed"""
        import os
        
        # Get absolute path - current_dir is already in vision folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        onnx_path = os.path.join(current_dir, "runs", "detect", "train2", "weights", "best.onnx")
        onnx_path = os.path.normpath(onnx_path)
        pt_path = os.path.join(current_dir, "runs", "detect", "train2", "weights", "best.pt")
        pt_path = os.path.normpath(pt_path)
        
        print(f"Vision: Looking for ONNX at {onnx_path}")
        print(f"Vision: File exists: {os.path.exists(onnx_path)}")
        
        # Check if ONNX exists, if not export from PT
        if not os.path.exists(onnx_path):
            print(f"Vision: ONNX not found, checking PT at {pt_path}")
            print(f"Vision: PT exists: {os.path.exists(pt_path)}")
            
            if os.path.exists(pt_path):
                print("Vision: Exporting from PyTorch to ONNX...")
                try:
                    from ultralytics import YOLO
                    model = YOLO(pt_path)
                    model.export(format='onnx', imgsz=640)
                    print("Vision: Export completed")
                except Exception as e:
                    print(f"Vision: Export failed - {e}")
                    return
            else:
                print(f"Vision: ERROR - Neither ONNX nor PT found!")
                return
        
        try:
            providers = ort.get_available_providers()
            if 'DmlExecutionProvider' in providers:
                selected = ['DmlExecutionProvider']
                print("Vision: Using AMD RX 470 DirectML")
            else:
                selected = ['CPUExecutionProvider']
                print("Vision: Using CPU")
            
            self.session = ort.InferenceSession(onnx_path, providers=selected)
            self.input_name = self.session.get_inputs()[0].name
            print("Vision: ONNX loaded successfully")
        except Exception as e:
            print(f"Vision: ONNX init failed - {e}")
            self.session = None
    
    def init_camera(self):
        """Initialize camera"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if self.cap.isOpened():
            print(f"Vision: Camera {self.camera_id} opened")
        else:
            print(f"Vision: Cannot open camera {self.camera_id}")
    
    def run(self):
        """Main loop in separate thread"""
        self.init_onnx()
        self.init_camera()
        
        if self.session is None or self.cap is None:
            print("Vision: Cannot start - init failed")
            return
        
        self.running = True
        print("Vision: Thread started")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Process with ONNX
            annotated, detections = self.process_frame(frame)
            
            # Convert to QPixmap
            pixmap = self.frame_to_pixmap(annotated)
            
            # Emit signal (safe to call from thread)
            self.pixmap_ready.emit(pixmap, detections)
            
            # ~30 FPS
            self.msleep(33)
        
        self.cap.release()
        print("Vision: Thread stopped")
    
    def process_frame(self, frame):
        """ONNX inference"""
        h, w = frame.shape[:2]
        
        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        
        # Inference
        outputs = self.session.run(None, {self.input_name: img})
        predictions = outputs[0][0].T
        
        # Process detections
        boxes, scores, class_ids = [], [], []
        for pred in predictions:
            class_scores = pred[4:]
            class_id = np.argmax(class_scores)
            conf = class_scores[class_id]
            
            if conf > 0.5:
                x, y, bw, bh = pred[0:4]
                x1 = int((x - bw/2) * w / 640)
                y1 = int((y - bh/2) * h / 640)
                boxes.append([x1, y1, int(bw * w / 640), int(bh * h / 640)])
                scores.append(float(conf))
                class_ids.append(class_id)
        
        # Draw results
        annotated = frame.copy()
        detections = []
        
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.3)
            for idx in indices.flatten():
                x1, y1, bw, bh = boxes[idx]
                class_name = self.class_names[class_ids[idx]]
                detections.append({'class': class_name, 'confidence': scores[idx]})
                cv2.rectangle(annotated, (x1, y1), (x1+bw, y1+bh), (0, 255, 0), 1)
                cv2.putText(annotated, f"{class_name} {scores[idx]:.2f}", 
                           (x1, y1-3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
        
        return annotated, detections
    
    def frame_to_pixmap(self, frame):
        """Convert OpenCV frame to QPixmap"""
        if frame is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qt_image)
    
    def stop(self):
        self.running = False
        self.wait()


class VisionController:
    """Controller to manage vision thread and update UI"""
    
    def __init__(self, label, camera_id=1):
        self.label = label
        self.thread = VisionThread(camera_id)
        self.thread.pixmap_ready.connect(self.on_pixmap_ready)
        self.latest_detections = []
    
    def on_pixmap_ready(self, pixmap, detections):
        """Called when new frame is ready (in main thread)"""
        if pixmap:
            # Scale to label size
            scaled = pixmap.scaled(self.label.size(), 
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(scaled)
        self.latest_detections = detections
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.thread.stop()
    
    def get_detections(self):
        return self.latest_detections
