"""Unattended Package & Abandoned Luggage Detector."""

from typing import List

import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class PackageDetector(BaseDetector):
    """Detects backpacks, suitcases, and unattended packages."""

    PACKAGE_LABELS = {"backpack", "handbag", "suitcase", "bag", "package", "parcel", "luggage"}

    def __init__(self, confidence_threshold: float = 0.5, enabled: bool = True):
        super().__init__(
            name="package",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="backpack"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        package_detections = []

        for d in raw_detections:
            lbl = d.label.lower()
            if any(p in lbl for p in self.PACKAGE_LABELS):
                d.category = "package"
                package_detections.append(d)

        return self.filter_by_confidence(package_detections)
