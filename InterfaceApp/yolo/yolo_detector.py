import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover
    YOLO = None


class YoloWebcamDetector:
    model_path: Path
    camera_id: int
    cap: Optional[Any]
    model: Optional[object]

    COLOR_MAP = {
        "circle": (0, 255, 255),
        "rectangle": (0, 0, 255),
        "delta": (255, 0, 0),
    }

    def __init__(self, model_path: str = "yolov12n.pt", camera_id: int = 0) -> None:
        self.model_path = Path(model_path)
        self.camera_id = camera_id
        self.cap: Optional[Any] = None
        self.model: Optional[Any] = None
        self._load_model()

    def _load_model(self) -> None:
        if YOLO is None:
            raise ImportError(
                "ultralytics is required for YOLO detection. Install with: pip install ultralytics"
            )

        self.model = YOLO(str(self.model_path))

    def start(self) -> bool:
        if cv2 is None:
            raise ImportError(
                "opencv-python is required for webcam capture. Install with: pip install opencv-python"
            )

        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera id={self.camera_id}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return True

    def stop(self) -> None:
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def read_frame(self) -> Optional[np.ndarray]:
        if self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        return frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        if self.model is None:
            return frame

        result = self.model(frame, imgsz=640, verbose=False)[0]
        annotated = frame.copy()
        self._annotate_result(annotated, result)
        return annotated

    def _annotate_result(self, frame: np.ndarray, result: Any) -> None:
        if result.boxes is None:
            return

        boxes = result.boxes.xyxy
        classes = result.boxes.cls
        scores = result.boxes.conf

        if hasattr(boxes, "cpu"):
            boxes = boxes.cpu().numpy()
        if hasattr(classes, "cpu"):
            classes = classes.cpu().numpy()
        if hasattr(scores, "cpu"):
            scores = scores.cpu().numpy()

        for box, cls_id, score in zip(boxes, classes, scores):
            x1, y1, x2, y2 = map(int, box.tolist())
            label = self._get_label(result, int(cls_id))
            color = self.COLOR_MAP.get(label, (255, 255, 255))

            if label == "circle":
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                radius = max(10, min((x2 - x1), (y2 - y1)) // 2)
                cv2.circle(frame, center, radius, color, 3)
                cv2.putText(
                    frame,
                    f"{label}:{score:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
            elif label == "rectangle":
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(
                    frame,
                    f"{label}:{score:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
            elif label == "delta":
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(
                    frame,
                    f"{label}:{score:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"{label}:{score:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

    def _get_label(self, result: Any, cls_id: int) -> str:
        names = getattr(result, "names", None)
        if isinstance(names, dict) and cls_id in names:
            return str(names[cls_id]).lower()
        try:
            return str(names[int(cls_id)]).lower()
        except Exception:
            return f"class_{cls_id}"

    def is_running(self) -> bool:
        return self.cap is not None and self.cap.isOpened()
