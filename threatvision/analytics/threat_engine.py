"""Threat Scoring & Fusion Engine."""

from enum import Enum
from typing import Dict, List, Tuple
from pydantic import BaseModel
from threatvision.models.backend import Detection


class ThreatLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatEvaluation(BaseModel):
    score: float  # 0.0 to 1.0 (0% - 100%)
    level: ThreatLevel
    primary_threat: str | None = None
    triggering_detections: List[Detection] = []
    recommendation: str = "System monitoring normally. Maintain standard vigilance."


# Threat weights mapping category / label to inherent hazard multiplier
CATEGORY_THREAT_WEIGHTS: Dict[str, float] = {
    "weapon": 0.95,
    "fire": 0.90,
    "smoke": 0.70,
    "fight": 0.85,
    "accident": 0.80,
    "fall": 0.65,
    "intrusion": 0.75,
    "crowd": 0.50,
    "package": 0.60,
    "person": 0.10,
    "vehicle": 0.15,
}


class ThreatEngine:
    """Combines multi-detector confidence outputs into calibrated threat score & level."""

    def __init__(
        self,
        threshold_low: float = 0.25,
        threshold_medium: float = 0.50,
        threshold_high: float = 0.75,
        threshold_critical: float = 0.90,
    ):
        self.threshold_low = threshold_low
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high
        self.threshold_critical = threshold_critical

    def evaluate(self, detections: List[Detection]) -> ThreatEvaluation:
        """Calculate threat score from frame detections."""
        if not detections:
            return ThreatEvaluation(
                score=0.0,
                level=ThreatLevel.SAFE,
                primary_threat=None,
                triggering_detections=[],
                recommendation="Area clear. Normal operations.",
            )

        max_score = 0.0
        primary_threat = None
        triggering = []

        for d in detections:
            category_weight = CATEGORY_THREAT_WEIGHTS.get(
                d.category, CATEGORY_THREAT_WEIGHTS.get(d.label.lower(), 0.2)
            )

            # Combined threat component: confidence * inherent threat weight
            raw_threat = d.confidence * category_weight

            if raw_threat > max_score:
                max_score = raw_threat
                primary_threat = f"{d.label} ({d.category})"

            if raw_threat >= self.threshold_low:
                triggering.append(d)

        # Multi-threat compounding: presence of multiple simultaneous threats boosts score
        if len(triggering) > 1:
            compounding_factor = min(0.15, 0.05 * (len(triggering) - 1))
            max_score = min(1.0, max_score + compounding_factor)

        # Classify threat level
        if max_score >= self.threshold_critical:
            level = ThreatLevel.CRITICAL
            rec = "CRITICAL ALERT: Immediate operator inspection and safety protocol activation required."
        elif max_score >= self.threshold_high:
            level = ThreatLevel.HIGH
            rec = "HIGH WARNING: Potential hazard detected. Human review recommended immediately."
        elif max_score >= self.threshold_medium:
            level = ThreatLevel.MEDIUM
            rec = "MODERATE NOTICE: Elevated activity observed. Monitor area closely."
        elif max_score >= self.threshold_low:
            level = ThreatLevel.LOW
            rec = "LOW NOTICE: Minor event detected. Proceed with normal monitoring."
        else:
            level = ThreatLevel.SAFE
            rec = "SAFE: Operational environment stable."

        return ThreatEvaluation(
            score=round(max_score, 3),
            level=level,
            primary_threat=primary_threat,
            triggering_detections=triggering,
            recommendation=rec,
        )
