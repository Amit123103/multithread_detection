"""Unit tests for IncidentManager and Storage."""

from pathlib import Path

import numpy as np

from threatvision.analytics.threat_engine import ThreatEvaluation, ThreatLevel
from threatvision.storage.incident_manager import IncidentManager


def test_record_incident(tmp_path: Path):
    mgr = IncidentManager(output_dir=str(tmp_path))
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    eval_result = ThreatEvaluation(
        score=0.95, level=ThreatLevel.CRITICAL, primary_threat="gun (weapon)"
    )

    incident_data = mgr.record_incident(dummy_frame, eval_result, camera_id=0)

    assert "incident_id" in incident_data
    assert Path(incident_data["screenshot_path"]).exists()
    assert mgr.csv_log_path.exists()

    history = mgr.get_history()
    assert len(history) >= 1
