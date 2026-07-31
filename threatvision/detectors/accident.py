"""Road Safety - Accident & Vehicle Crash Detector."""

from typing import List
import numpy as np
from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory
from threatvision.utils.geometry import compute_iou


class AccidentDetector(BaseDetector):
    """Detects vehicle crashes and collisions based on bounding box overlap and dynamics."""

    def __init__(self, confidence_threshold: float = 0.6, enabled: bool = True):
        super().__init__(
            name="accident",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="accident"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        accident_detections: List[Detection] = []

        # Check IoU between multiple vehicle boxes for high-overlap potential collisions
        vehicles = [d for d in raw_detections if d.category == "vehicle" or d.label in ("car", "truck", "bus")]

        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                boxA = vehicles[i].box
                boxB = vehicles[j].box
                iou = compute_iou(boxA, boxB)
                if iou > 0.45:  # High overlapping vehicle bounding boxes
                    merged_box = (
                        min(boxA[0], boxB[0]),
                        min(boxA[1], boxB[1]),
                        max(boxA[2], boxB[2]),
                        max(boxA[3], boxB[3]),
                    )
                    accident_detections.append(
                        Detection(
                            label="accident",
                            confidence=min(0.95, iou + 0.3),
                            box=merged_box,
                            category="road_safety",
                            attributes={"collision_iou": iou},
                        )
                    )

        if not accident_detections:
            for d in raw_detections:
                if d.label.lower() in ("accident", "crash", "collision"):
                    d.category = "road_safety"
                    accident_detections.append(d)

        return self.filter_by_confidence(accident_detections)
