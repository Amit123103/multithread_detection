"""Restricted Area Intrusion & Loitering Detector."""

from typing import List, Tuple

import numpy as np

from threatvision.detectors.base import BaseDetector
from threatvision.models.backend import Detection, ModelFactory
from threatvision.utils.geometry import box_centroid, point_in_polygon


class IntrusionDetector(BaseDetector):
    """Detects entry into user-configured perimeter polygon zones."""

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
        restricted_polygons: List[List[Tuple[int, int]]] | None = None,
    ):
        super().__init__(
            name="intrusion",
            confidence_threshold=confidence_threshold,
            enabled=enabled,
            backend=ModelFactory.create_backend(target_label="person"),
        )
        self.restricted_polygons = restricted_polygons or []

    def set_restricted_polygons(self, polygons: List[List[Tuple[int, int]]]) -> None:
        self.restricted_polygons = polygons

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled or not self.restricted_polygons:
            return []

        raw_detections = self.backend.predict(frame)
        intrusion_detections: List[Detection] = []

        for d in raw_detections:
            center = box_centroid(d.box)
            for zone_idx, poly in enumerate(self.restricted_polygons):
                if point_in_polygon(center, poly):
                    intrusion_detections.append(
                        Detection(
                            label="intrusion",
                            confidence=d.confidence,
                            box=d.box,
                            category="behavior",
                            attributes={
                                "zone_id": zone_idx,
                                "violator_label": d.label,
                                "centroid": center,
                            },
                        )
                    )
                    break

        return self.filter_by_confidence(intrusion_detections)
