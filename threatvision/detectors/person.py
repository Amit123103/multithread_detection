"""Person detection module."""

from typing import List
import numpy as np
from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class PersonDetector(BaseDetector):
    """Detects human presence in frame."""

    def __init__(self, confidence_threshold: float = 0.5, enabled: bool = True):
        super().__init__(
            name="person",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="person"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        person_detections = [
            d for d in raw_detections if d.label.lower() in ("person", "human")
        ]
        for d in person_detections:
            d.category = "person"

        return self.filter_by_confidence(person_detections)
