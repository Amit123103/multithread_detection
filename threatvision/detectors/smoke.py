"""Smoke detection module."""

from typing import List

import cv2
import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class SmokeDetector(BaseDetector):
    """Detects smoke hazards in frame using contrast/chrominance analytics and model backend."""

    def __init__(self, confidence_threshold: float = 0.55, enabled: bool = True):
        super().__init__(
            name="smoke",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="smoke"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        # Smoke vision heuristic: low saturation, gray intensity range
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_smoke = np.array([0, 0, 100], dtype=np.uint8)
        upper_smoke = np.array([180, 50, 220], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_smoke, upper_smoke)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: List[Detection] = []

        h, w = frame.shape[:2]
        frame_area = h * w

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > frame_area * 0.03:  # Only significant smoke plumes
                x, y, bw, bh = cv2.boundingRect(cnt)
                conf = min(0.90, area / (frame_area * 0.2))
                detections.append(
                    Detection(
                        label="smoke",
                        confidence=conf,
                        box=(x, y, x + bw, y + bh),
                        category="environmental",
                    )
                )

        if not detections:
            raw_backend = self.backend.predict(frame)
            for d in raw_backend:
                if d.label.lower() in ("smoke", "haze"):
                    d.category = "environmental"
                    detections.append(d)

        return self.filter_by_confidence(detections)
