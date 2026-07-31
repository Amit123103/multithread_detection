"""Behavior Detection - Fight & Physical Violence Detector."""

from typing import List

import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory
from threatvision.utils.geometry import compute_iou


class FightDetector(BaseDetector):
    """Detects physical fights, violent altercations, and aggressive movements."""

    def __init__(self, confidence_threshold: float = 0.6, enabled: bool = True):
        super().__init__(
            name="fight",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="fight"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        fight_detections: List[Detection] = []

        # Analyze close proximity / overlapping person bounding boxes
        persons = [d for d in raw_detections if d.label.lower() in ("person", "human")]

        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                box_a = persons[i].box
                box_b = persons[j].box
                iou = compute_iou(box_a, box_b)
                if iou > 0.35:  # Close physical contact/entanglement
                    merged_box = (
                        min(box_a[0], box_b[0]),
                        min(box_a[1], box_b[1]),
                        max(box_a[2], box_b[2]),
                        max(box_a[3], box_b[3]),
                    )
                    fight_detections.append(
                        Detection(
                            label="fight",
                            confidence=min(0.92, iou + 0.4),
                            box=merged_box,
                            category="behavior",
                            attributes={"interaction_intensity": iou},
                        )
                    )

        if not fight_detections:
            for d in raw_detections:
                if d.label.lower() in ("fight", "brawl", "violence"):
                    d.category = "behavior"
                    fight_detections.append(d)

        return self.filter_by_confidence(fight_detections)
