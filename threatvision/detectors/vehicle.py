"""Vehicle detection module (Car, Truck, Bus, Motorcycle, Bicycle)."""

from typing import List
import numpy as np
from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class VehicleDetector(BaseDetector):
    """Detects motorized vehicles and bicycles."""

    VEHICLE_LABELS = {"car", "truck", "bus", "motorcycle", "motorbike", "bicycle", "vehicle"}

    def __init__(self, confidence_threshold: float = 0.5, enabled: bool = True):
        super().__init__(
            name="vehicle",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="car"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        vehicle_detections = []

        for d in raw_detections:
            lbl = d.label.lower()
            if any(v in lbl for v in self.VEHICLE_LABELS):
                d.category = "vehicle"
                vehicle_detections.append(d)

        return self.filter_by_confidence(vehicle_detections)
