"""Weapon detection module (Gun, Knife, Rifle)."""

from typing import List

import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class WeaponDetector(BaseDetector):
    """Detects dangerous weapons (handguns, knives, rifles)."""

    WEAPON_LABELS = {
        "gun",
        "handgun",
        "pistol",
        "rifle",
        "firearm",
        "knife",
        "weapon",
        "blade",
    }

    def __init__(self, confidence_threshold: float = 0.6, enabled: bool = True):
        super().__init__(
            name="weapon",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="gun"),
        )

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        weapon_detections = []

        for d in raw_detections:
            lbl = d.label.lower()
            if any(w in lbl for w in self.WEAPON_LABELS) or lbl == "weapon":
                d.category = "weapon"
                weapon_detections.append(d)

        return self.filter_by_confidence(weapon_detections)
