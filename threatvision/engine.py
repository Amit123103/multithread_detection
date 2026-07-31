"""ThreatVision AI Core Engine."""

import threading
import time
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from threatvision.alerts.alert_types import AlertMessage, AlertSeverity
from threatvision.analytics.spatial import SpatialAnalytics
from threatvision.analytics.threat_engine import (
    ThreatEngine,
    ThreatEvaluation,
    ThreatLevel,
)
from threatvision.camera.stream import CameraStream
from threatvision.config.config import ThreatVisionConfig
from threatvision.detectors.accident import AccidentDetector
from threatvision.detectors.base import BaseDetector
from threatvision.detectors.crowd import CrowdDetector
from threatvision.detectors.fall import FallDetector
from threatvision.detectors.fight import FightDetector
from threatvision.detectors.fire import FireDetector
from threatvision.detectors.intrusion import IntrusionDetector
from threatvision.detectors.package import PackageDetector
from threatvision.detectors.person import PersonDetector
from threatvision.detectors.smoke import SmokeDetector
from threatvision.detectors.vehicle import VehicleDetector
from threatvision.detectors.weapon import WeaponDetector
from threatvision.logging.logger import setup_logger
from threatvision.models.backend import Detection
from threatvision.notifications.dispatcher import NotificationDispatcher
from threatvision.reports.pdf_exporter import PDFReportExporter
from threatvision.storage.incident_manager import IncidentManager
from threatvision.tracking.tracker import Tracker
from threatvision.utils.draw import draw_bounding_box, draw_hud
from threatvision.utils.metrics import PerformanceMonitor

logger = setup_logger("threatvision")


class ThreatVision:
    """
    Primary API entry point for ThreatVision AI real-time threat detection framework.

    Example:
    ```python
    from threatvision import ThreatVision

    tv = ThreatVision(camera=0, dashboard=True, save_incidents=True)
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()
    tv.enable_fight_detection()
    tv.enable_smoke_detection()
    tv.start()
    ```
    """

    def __init__(
        self,
        camera: Union[int, str] = 0,
        rtsp: Optional[str] = None,
        video: Optional[str] = None,
        image: Optional[str] = None,
        config: Optional[ThreatVisionConfig] = None,
        dashboard: bool = False,
        save_incidents: bool = True,
        output_dir: str = "incidents",
    ):
        self.config = config or ThreatVisionConfig()

        # Determine camera source priority
        if rtsp:
            self.source = rtsp
        elif video:
            self.source = video
        elif image:
            self.source = image
        else:
            self.source = camera

        self.stream = CameraStream(
            source=self.source,
            skip_frames=self.config.camera.skip_frames,
            width=self.config.camera.width,
            height=self.config.camera.height,
        )

        self.detectors: Dict[str, BaseDetector] = {}
        self.tracker = Tracker()
        self.threat_engine = ThreatEngine(
            threshold_low=self.config.analytics.threat_threshold_low,
            threshold_medium=self.config.analytics.threat_threshold_medium,
            threshold_high=self.config.analytics.threat_threshold_high,
            threshold_critical=self.config.analytics.threat_threshold_critical,
        )
        self.spatial = SpatialAnalytics()
        self.incident_manager = IncidentManager(output_dir=output_dir) if save_incidents else None
        self.pdf_exporter = PDFReportExporter(output_dir=f"{output_dir}/reports")
        self.dispatcher = NotificationDispatcher(self.config.notifications)
        self.perf_monitor = PerformanceMonitor()

        self.dashboard_enabled = dashboard
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

        self.latest_raw_frame: Optional[np.ndarray] = None
        self.latest_annotated_frame: Optional[np.ndarray] = None
        self.latest_evaluation: ThreatEvaluation = ThreatEvaluation(
            score=0.0, level=ThreatLevel.SAFE
        )
        self.latest_detections: List[Detection] = []
        self.fps = 0.0

    # Detector Enablers
    def enable_person_detection(self, threshold: float = 0.5) -> "ThreatVision":
        self.detectors["person"] = PersonDetector(confidence_threshold=threshold)
        return self

    def enable_weapon_detection(self, threshold: float = 0.6) -> "ThreatVision":
        self.detectors["weapon"] = WeaponDetector(confidence_threshold=threshold)
        return self

    def enable_fire_detection(self, threshold: float = 0.55) -> "ThreatVision":
        self.detectors["fire"] = FireDetector(confidence_threshold=threshold)
        return self

    def enable_smoke_detection(self, threshold: float = 0.55) -> "ThreatVision":
        self.detectors["smoke"] = SmokeDetector(confidence_threshold=threshold)
        return self

    def enable_vehicle_detection(self, threshold: float = 0.5) -> "ThreatVision":
        self.detectors["vehicle"] = VehicleDetector(confidence_threshold=threshold)
        return self

    def enable_accident_detection(self, threshold: float = 0.6) -> "ThreatVision":
        self.detectors["accident"] = AccidentDetector(confidence_threshold=threshold)
        return self

    def enable_fight_detection(self, threshold: float = 0.6) -> "ThreatVision":
        self.detectors["fight"] = FightDetector(confidence_threshold=threshold)
        return self

    def enable_fall_detection(self, threshold: float = 0.55) -> "ThreatVision":
        self.detectors["fall"] = FallDetector(confidence_threshold=threshold)
        return self

    def enable_intrusion_detection(
        self, threshold: float = 0.5, restricted_zones: Optional[List] = None
    ) -> "ThreatVision":
        detector = IntrusionDetector(confidence_threshold=threshold)
        if restricted_zones:
            detector.set_restricted_polygons(restricted_zones)
        self.detectors["intrusion"] = detector
        return self

    def enable_crowd_detection(self, threshold: float = 0.5) -> "ThreatVision":
        self.detectors["crowd"] = CrowdDetector(confidence_threshold=threshold)
        return self

    def enable_package_detection(self, threshold: float = 0.5) -> "ThreatVision":
        self.detectors["package"] = PackageDetector(confidence_threshold=threshold)
        return self

    def add_custom_detector(self, detector: BaseDetector) -> "ThreatVision":
        self.detectors[detector.name] = detector
        return self

    def process_single_frame(
        self, frame: np.ndarray
    ) -> Tuple[ThreatEvaluation, List[Detection]]:
        """Process a single image frame and return evaluation results."""
        all_detections: List[Detection] = []

        start_time = time.time()

        # Run active detectors
        for name, detector in self.detectors.items():
            if detector.enabled:
                try:
                    dets = detector.detect(frame)
                    all_detections.extend(dets)
                except Exception as e:
                    logger.error(f"Detector [{name}] error: {e}")

        # Update tracking
        tracked_detections = self.tracker.update(all_detections, frame.shape[:2])

        # Threat evaluation
        evaluation = self.threat_engine.evaluate(tracked_detections)

        # Monitor latency
        self.fps = self.perf_monitor.tock(time.time() - start_time)

        return evaluation, tracked_detections

    def start(self, block: bool = False) -> None:
        """Start camera feed and real-time threat detection loop."""
        if self.is_running:
            logger.warning("ThreatVision engine is already running.")
            return

        if not self.detectors:
            logger.info("No detectors explicitly enabled. Enabling default person & weapon detectors.")
            self.enable_person_detection()
            self.enable_weapon_detection()

        self.stream.start()
        self.is_running = True

        if self.dashboard_enabled:
            self._launch_dashboard_server()

        logger.info(f"ThreatVision AI Engine started on source: {self.source}")

        if block:
            self._run_loop()
        else:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def _run_loop(self) -> None:
        while self.is_running:
            self.perf_monitor.tick()
            ret, frame = self.stream.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            self.latest_raw_frame = frame
            evaluation, detections = self.process_single_frame(frame)
            self.latest_evaluation = evaluation
            self.latest_detections = detections

            # Render annotations
            annotated = frame.copy()
            for d in detections:
                color = (0, 0, 255) if evaluation.level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL) else (0, 255, 0)
                draw_bounding_box(
                    annotated,
                    box=d.box,
                    label=d.label,
                    confidence=d.confidence,
                    color=color,
                    track_id=d.track_id,
                )

            draw_hud(
                annotated,
                fps=self.fps,
                threat_score=evaluation.score,
                threat_level=evaluation.level.value,
                active_alerts_count=len(evaluation.triggering_detections),
            )

            self.latest_annotated_frame = annotated

            # Handle Incident Storage & Alerts on High/Critical Threat
            if evaluation.level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
                if self.incident_manager:
                    inc_data = self.incident_manager.record_incident(
                        annotated, evaluation, camera_id=self.source
                    )
                    # Generate PDF report
                    try:
                        self.pdf_exporter.generate_report(inc_data)
                    except Exception as e:
                        logger.warning(f"PDF export failed: {e}")

                # Dispatch Alert
                alert_msg = AlertMessage(
                    title=f"HAZARD DETECTED: {evaluation.primary_threat}",
                    body=evaluation.recommendation,
                    severity=AlertSeverity.CRITICAL if evaluation.level == ThreatLevel.CRITICAL else AlertSeverity.HIGH,
                    threat_score=evaluation.score,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                )
                self.dispatcher.dispatch(alert_msg)

            time.sleep(0.01)

    def _launch_dashboard_server(self) -> None:
        import uvicorn

        from threatvision.api.app import app, set_engine_instance

        set_engine_instance(self)

        def run_uvicorn():
            uvicorn.run(
                app,
                host=self.config.host,
                port=self.config.dashboard_port,
                log_level="warning",
            )

        t = threading.Thread(target=run_uvicorn, daemon=True)
        t.start()
        logger.info(
            f"Dashboard live at http://{self.config.host}:{self.config.dashboard_port}"
        )

    def stop(self) -> None:
        """Stop processing engine and release camera stream."""
        self.is_running = False
        self.stream.release()
        logger.info("ThreatVision AI Engine stopped.")

    def get_statistics(self) -> Dict:
        return {
            "fps": round(self.fps, 1),
            "threat_score": self.latest_evaluation.score,
            "threat_level": self.latest_evaluation.level.value,
            "primary_threat": self.latest_evaluation.primary_threat,
            "active_detections_count": len(self.latest_detections),
            "tracked_objects_count": len(self.tracker.tracked_objects),
        }
