"""Behavior Detection - Fall & Person Lying Down Detector."""

from typing import List
import numpy as np
from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class FallDetector(BaseDetector):
    """Detects person falling over or lying down on the floor/ground."""

    def __init__(self, confidence_threshold: float = 0.55, enabled: bool = True):
        super().__init__(
            name="fall",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="fall"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        fall_detections: List[Detection] = []

        # Analyze bounding box aspect ratio (width > height indicates horizontal lying/fall posture)
        persons = [d for d in raw_detections if d.label.lower() in ("person", "human")]

        for p in persons:
            xmin, ymin, xmax, ymax = p.box
            bw = xmax - xmin
            bh = ymax - ymin
            aspect_ratio = float(bw) / float(bh) if bh > 0 else 1.0

            if aspect_ratio > 1.25:  # Person is lying horizontally
                fall_detections.append(
                    Detection(
                        label="fall",
                        confidence=min(0.95, p.confidence * 1.1),
                        box=p.box,
                        category="behavior",
                        attributes={"aspect_ratio": aspect_ratio, "state": "lying_down"},
                    )
                )

        if not fall_detections:
            for d in raw_detections:
                if d.label.lower() in ("fall", "fallen", "lying"):
                    d.category = "behavior"
                    fall_detections.append(d)

        return self.filter_by_confidence(fall_detections)
