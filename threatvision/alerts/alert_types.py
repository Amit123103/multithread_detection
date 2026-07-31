"""Alert definitions and types."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
from threatvision.analytics.threat_engine import ThreatEvaluation


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertMessage(BaseModel):
    title: str
    body: str
    severity: AlertSeverity
    threat_score: float
    timestamp: str
    incident_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
