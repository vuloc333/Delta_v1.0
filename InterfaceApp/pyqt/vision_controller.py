from typing import Any, Optional, Tuple

import numpy as np

from yolo.yolo_detector import YoloWebcamDetector


class VisionController:
    def __init__(self, model_path: str = "yolov12n.pt", camera_id: int = 0) -> None:
        self._model_path = model_path
        self._camera_id = camera_id
        self._detector: Optional[YoloWebcamDetector] = None
        self._error: Optional[str] = None

    def start(self) -> Tuple[bool, str]:
        if self._detector is not None:
            return True, "Webcam already running"

        try:
            self._detector = YoloWebcamDetector(model_path=self._model_path, camera_id=self._camera_id)
            self._detector.start()
            return True, "Webcam started"
        except Exception as exc:
            self._detector = None
            self._error = str(exc)
            return False, self._error

    def stop(self) -> None:
        if self._detector is None:
            return

        try:
            self._detector.stop()
        except Exception:
            pass
        finally:
            self._detector = None

    def is_running(self) -> bool:
        return self._detector is not None and self._detector.is_running()

    def read_frame(self) -> Optional[np.ndarray]:
        if self._detector is None:
            return None

        return self._detector.read_frame()

    def annotate_frame(self, frame: np.ndarray) -> np.ndarray:
        if self._detector is None:
            return frame

        return self._detector.process_frame(frame)
