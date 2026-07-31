"""Fire detection module."""

from typing import List

import cv2
import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class FireDetector(BaseDetector):
    """Detects fire visual hazards in frame using deep learning or HSV color space analytics."""

    def __init__(self, confidence_threshold: float = 0.55, enabled: bool = True):
        super().__init__(
            name="fire",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="fire"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        # Color-space analysis fallback for real-time fire detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_fire = np.array([18, 50, 50], dtype=np.uint8)
        upper_fire = np.array([35, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_fire, upper_fire)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: List[Detection] = []

        h, w = frame.shape[:2]
        frame_area = h * w

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > frame_area * 0.01:  # Only significant fire patches
                x, y, bw, bh = cv2.boundingRect(cnt)
                conf = min(0.95, float(area / (frame_area * 0.1)))
                detections.append(
                    Detection(
                        label="fire",
                        confidence=conf,
                        box=(x, y, x + bw, y + bh),
                        category="environmental",
                    )
                )

        if not detections:
            # Check backend fallback
            raw_backend = self.backend.predict(frame)
            for d in raw_backend:
                if d.label.lower() in ("fire", "flame"):
                    d.category = "environmental"
                    detections.append(d)

        return self.filter_by_confidence(detections)
