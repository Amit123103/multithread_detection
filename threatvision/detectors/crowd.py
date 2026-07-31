"""Crowd Panic & High Density Crowd Detector."""

from typing import List

import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory


class CrowdDetector(BaseDetector):
    """Detects high-density crowd gatherings and potential crowd panic surge."""

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
        density_threshold: int = 5,
    ):
        super().__init__(
            name="crowd",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="person"),
        )
        self.density_threshold = density_threshold

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []

        raw_detections = self.backend.predict(frame)
        persons = [d for d in raw_detections if d.label.lower() in ("person", "human")]

        if len(persons) >= self.density_threshold:
            # Calculate bounding bounding-box containing crowd cluster
            xmin = min(p.box[0] for p in persons)
            ymin = min(p.box[1] for p in persons)
            xmax = max(p.box[2] for p in persons)
            ymax = max(p.box[3] for p in persons)

            crowd_confidence = min(0.98, len(persons) / (self.density_threshold * 2))

            return self.filter_by_confidence(
                [
                    Detection(
                        label="crowd",
                        confidence=crowd_confidence,
                        box=(xmin, ymin, xmax, ymax),
                        category="behavior",
                        attributes={
                            "person_count": len(persons),
                            "density_alert": True,
                        },
                    )
                ]
            )

        return []
