import cv2
import numpy as np
import onnxruntime as ort

class RX470Tester:
    def __init__(self, model_path=r"runs\detect\train2\weights\best.onnx"):
        # Setup DirectML for AMD RX 470
        providers = ort.get_available_providers()
        print(f"Available providers: {providers}")
        
        if 'DmlExecutionProvider' in providers:
            selected = ['DmlExecutionProvider']
            print("Using AMD RX 470 with DirectML")
        else:
            selected = ['CPUExecutionProvider']
            print("DirectML not available, using CPU")
        
        self.session = ort.InferenceSession(model_path, providers=selected)
        self.input_name = self.session.get_inputs()[0].name
        self.class_names = ['BlueTri', 'RedRec', 'YelCir']
        
        # Open webcam
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            exit()
        
        print("RX 470 Test started. Press 'q' to quit.")
    
    def process_frame(self, frame):
        h, w = frame.shape[:2]
        
        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        
        # ONNX inference on RX 470
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
                detections.append(f"{class_name}:{scores[idx]:.2f}")
                cv2.rectangle(annotated, (x1, y1), (x1+bw, y1+bh), (0, 255, 0), 1)
                cv2.putText(annotated, f"{class_name} {scores[idx]:.2f}", 
                           (x1, y1-3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
        
        return annotated, detections
    
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            annotated, detections = self.process_frame(frame)
            
            # Print detections
            if detections:
                print(" | ".join(detections))
            
            cv2.imshow("RX 470 YOLO Test", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("Test finished.")

def main():
    tester = RX470Tester()
    tester.run()

if __name__ == "__main__":
    main()
