"""FastAPI REST API and WebSockets server for ThreatVision AI."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import cv2
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from pydantic import BaseModel

from threatvision.analytics.threat_engine import ThreatEvaluation, ThreatLevel
from threatvision.dashboard import STATIC_DIR
from threatvision.models.backend import Detection
from threatvision.storage.incident_manager import IncidentManager
from threatvision.utils.metrics import PerformanceMonitor

app = FastAPI(
    title="ThreatVision AI API",
    description="Production REST & WebSocket API for real-time computer vision threat detection framework.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Dashboard Mount
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Shared Engine Instances
_incident_manager = IncidentManager()
_performance_monitor = PerformanceMonitor()
_global_engine = None  # Reference to running ThreatVision instance if registered


class DetectionResponse(BaseModel):
    threat_score: float
    threat_level: str
    primary_threat: Optional[str]
    detections: List[Dict[str, Any]]
    recommendation: str


def set_engine_instance(engine: Any) -> None:
    """Register active ThreatVision engine instance with FastAPI app."""
    global _global_engine
    _global_engine = engine


@app.get("/", response_class=HTMLResponse)
async def get_dashboard() -> HTMLResponse:
    """Serve threatvision dashboard UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>ThreatVision AI API Active</h1>")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "engine_active": _global_engine is not None and _global_engine.is_running,
    }


@app.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Fetch real-time telemetry statistics, FPS, and resource utilization."""
    if _global_engine is not None:
        stats = _global_engine.get_statistics()
        stats["system"] = PerformanceMonitor.get_system_resources()
        return stats

    return {
        "fps": 30.0,
        "threat_score": 0.0,
        "threat_level": "SAFE",
        "active_detections_count": 0,
        "system": PerformanceMonitor.get_system_resources(),
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_frame(file: UploadFile = File(...)) -> DetectionResponse:
    """Run real-time threat detection on an uploaded image file."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file format")

    if _global_engine is not None:
        eval_result, detections = _global_engine.process_single_frame(frame)
    else:
        # Fallback processing
        from threatvision.analytics.threat_engine import ThreatEngine
        from threatvision.detectors.person import PersonDetector

        detector = PersonDetector()
        detections = detector.detect(frame)
        engine = ThreatEngine()
        eval_result = engine.evaluate(detections)

    return DetectionResponse(
        threat_score=eval_result.score,
        threat_level=eval_result.level.value,
        primary_threat=eval_result.primary_threat,
        detections=[
            {
                "label": d.label,
                "confidence": d.confidence,
                "box": list(d.box),
                "category": d.category,
            }
            for d in detections
        ],
        recommendation=eval_result.recommendation,
    )


@app.get("/history")
async def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve security incident history log."""
    return _incident_manager.get_history(limit=limit)


@app.get("/history/csv")
async def get_csv_history() -> FileResponse:
    """Export security incident log as CSV file download."""
    csv_path = _incident_manager.csv_log_path
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Incident history log empty")
    return FileResponse(
        path=csv_path, media_type="text/csv", filename="incident_history.csv"
    )


@app.get("/stream")
async def video_feed() -> StreamingResponse:
    """Live Video Feed Streaming via multipart MJPEG boundary."""
    def frame_generator():
        while True:
            if _global_engine is not None and _global_engine.latest_annotated_frame is not None:
                frame = _global_engine.latest_annotated_frame
            else:
                # Generate black placeholder frame when camera idle
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "CAMERA FEED IDLE",
                    (180, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            import time
            time.sleep(0.033)

    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
