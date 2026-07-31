"""Configuration manager for ThreatVision AI."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class CameraConfig(BaseModel):
    source: str | int = 0
    fps: int = 30
    width: int = 1280
    height: int = 720
    skip_frames: int = 0
    reconnect_attempts: int = 5


class DetectorConfig(BaseModel):
    model_config = {"protected_namespaces": ()}
    enabled: bool = True
    confidence_threshold: float = 0.5
    model_name: str = "default"
    device: str = "cpu"  # 'cpu', 'cuda', 'onnx'


class AnalyticsConfig(BaseModel):
    threat_threshold_low: float = 0.25
    threat_threshold_medium: float = 0.50
    threat_threshold_high: float = 0.75
    threat_threshold_critical: float = 0.90
    restricted_zones: List[List[List[int]]] = Field(default_factory=list)


class StorageConfig(BaseModel):
    save_incidents: bool = True
    output_dir: str = "incidents"
    record_clips: bool = True
    clip_duration_seconds: int = 10
    save_pdf_reports: bool = True


class NotificationConfig(BaseModel):
    enable_desktop: bool = False
    enable_webhook: bool = False
    webhook_url: Optional[str] = None
    email_smtp: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None


class ThreatVisionConfig(BaseSettings):
    camera: CameraConfig = Field(default_factory=CameraConfig)
    detectors: Dict[str, DetectorConfig] = Field(
        default_factory=lambda: {
            "person": DetectorConfig(confidence_threshold=0.5),
            "weapon": DetectorConfig(confidence_threshold=0.6),
            "fire": DetectorConfig(confidence_threshold=0.55),
            "smoke": DetectorConfig(confidence_threshold=0.55),
            "vehicle": DetectorConfig(confidence_threshold=0.5),
            "accident": DetectorConfig(confidence_threshold=0.6),
            "fight": DetectorConfig(confidence_threshold=0.6),
            "fall": DetectorConfig(confidence_threshold=0.55),
            "intrusion": DetectorConfig(confidence_threshold=0.5),
            "crowd": DetectorConfig(confidence_threshold=0.5),
            "package": DetectorConfig(confidence_threshold=0.5),
        }
    )
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    dashboard_port: int = 8000
    host: str = "127.0.0.1"

    @classmethod
    def load_from_file(cls, file_path: str | Path) -> "ThreatVisionConfig":
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        ext = path.suffix.lower()
        content: Dict[str, Any] = {}

        if ext in (".yaml", ".yml"):
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}
        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)
        elif ext == ".toml":
            try:
                import tomllib  # Python 3.11+

                with open(path, "rb") as f:
                    content = tomllib.load(f)
            except ImportError:
                import tomli

                with open(path, "rb") as f:
                    content = tomli.load(f)
        else:
            raise ValueError(f"Unsupported config format: {ext}")

        return cls(**content)

    def save_to_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        ext = path.suffix.lower()
        data = self.model_dump()

        if ext in (".yaml", ".yml"):
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)
        elif ext == ".json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {ext}")
