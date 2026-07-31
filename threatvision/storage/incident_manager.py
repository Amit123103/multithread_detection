"""Incident Manager for automated screenshot capture, JSON logging, CSV exporting, and video clips."""

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from threatvision.analytics.threat_engine import ThreatEvaluation


class IncidentManager:
    """Handles incident recording, disk storage, JSON log generation, and CSV exports."""

    def __init__(self, output_dir: str = "incidents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_log_path = self.output_dir / "incident_history.csv"
        self._init_csv()

    def _init_csv(self) -> None:
        if not self.csv_log_path.exists():
            with open(self.csv_log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Incident_ID",
                        "Timestamp",
                        "Threat_Level",
                        "Threat_Score",
                        "Primary_Threat",
                        "Screenshot_Path",
                    ]
                )

    def record_incident(
        self,
        frame: np.ndarray,
        evaluation: ThreatEvaluation,
        camera_id: str | int = 0,
        gps_coords: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        """Save screenshot, metadata JSON, and update CSV incident log."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        incident_id = f"INC-{timestamp_str}"

        # Save screenshot
        img_filename = f"{incident_id}.jpg"
        img_path = self.output_dir / img_filename
        cv2.imwrite(str(img_path), frame)

        # JSON Metadata
        incident_data = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "camera_id": str(camera_id),
            "gps": gps_coords,
            "threat_level": evaluation.level.value,
            "threat_score": evaluation.score,
            "primary_threat": evaluation.primary_threat,
            "recommendation": evaluation.recommendation,
            "screenshot_path": str(img_path),
            "detections": [
                {
                    "label": d.label,
                    "confidence": d.confidence,
                    "box": list(d.box),
                    "category": d.category,
                }
                for d in evaluation.triggering_detections
            ],
        }

        json_path = self.output_dir / f"{incident_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(incident_data, f, indent=2)

        # Append to CSV
        with open(self.csv_log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    incident_id,
                    incident_data["timestamp"],
                    evaluation.level.value,
                    evaluation.score,
                    evaluation.primary_threat,
                    str(img_path),
                ]
            )

        return incident_data

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent incident records from JSON logs."""
        incidents = []
        json_files = sorted(self.output_dir.glob("INC-*.json"), reverse=True)[:limit]
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    incidents.append(json.load(f))
            except Exception:
                continue
        return incidents
