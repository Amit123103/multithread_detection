"""Base detector interface for all threat vision detectors."""

from abc import ABC, abstractmethod
from typing import List

import numpy as np

from threatvision.models.backend import Detection, ModelBackend, ModelFactory


class BaseDetector(ABC):
    """Abstract Base Class for all ThreatVision detectors."""

    def __init__(
        self,
        name: str,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
        backend: ModelBackend | None = None,
    ):
        self.name = name
        self.confidence_threshold = confidence_threshold
        self.enabled = enabled
        self.backend = backend or ModelFactory.create_backend(target_label=self.name)

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Process image frame and return list of detections."""
        pass

    def filter_by_confidence(self, detections: List[Detection]) -> List[Detection]:
        """Filter detections below configured confidence threshold."""
        return [d for d in detections if d.confidence >= self.confidence_threshold]
