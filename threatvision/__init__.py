"""
ThreatVision AI — Production-Grade Real-Time AI Computer Vision Threat Detection Framework.

Import usage:
```python
from threatvision import ThreatVision, ThreatLevel
```
"""

from threatvision.analytics.threat_engine import ThreatEvaluation, ThreatLevel
from threatvision.detectors.base import BaseDetector
from threatvision.engine import ThreatVision
from threatvision.models.backend import Detection
from threatvision.plugins import Plugin, register_plugin

__version__ = "1.0.0"

__all__ = [
    "ThreatVision",
    "ThreatLevel",
    "ThreatEvaluation",
    "Detection",
    "BaseDetector",
    "Plugin",
    "register_plugin",
    "__version__",
]
