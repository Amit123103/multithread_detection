<div align="center">

# 🛡️ ThreatVision AI (`threatvision-ai`)

**Production-Grade, Open-Source AI Real-Time Computer Vision Threat Detection & Safety Framework**

[![PyPI version](https://img.shields.io/pypi/v/threatvision-ai.svg?color=blue)](https://pypi.org/project/threatvision-ai/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/threatvision/threatvision-ai/ci.yml?branch=main)](https://github.com/threatvision/threatvision-ai/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/threatvision/threatvision-ai)

</div>

---

## 🌟 Overview

**ThreatVision AI** is a modular, high-performance computer vision security framework designed to analyze live video streams from webcams, RTSP IP cameras, CCTV feeds, and video files to detect safety hazards, weapons, physical altercations, fires, intrusions, and vehicle collisions in real time.

> [!IMPORTANT]
> **Safety & Operator Assistance Disclaimer**: ThreatVision AI is engineered strictly as an **operator assistance tool**. Detections represent calibrated probability estimates and threat levels rather than absolute assertions. The framework is designed to assist human security operators, not to replace human judgment or make autonomous safety decisions.

---

## 🚀 Key Features

* 📷 **Universal Camera Support**: Webcams, USB cameras, RTSP streams, CCTV, IP cameras, video files, single images, multi-camera setups.
* 🤖 **Modular AI Detectors**: 11 specialized detectors including Person, Weapon (Gun/Knife/Rifle), Fire, Smoke, Vehicle, Accident/Collision, Fight/Violence, Fall/Lying Down, Zone Intrusion, Crowd Panic, Unattended Package.
* 🎯 **Multi-Object Tracking**: Persistent IDs, entry/exit counting, spatial heatmaps, trajectory tracking, loitering dwell time calculations.
* 🧮 **Threat Scoring Engine**: Multi-detector fusion matrix generating calibrated Threat Scores (0–100%) and Threat Levels (`SAFE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
* 🚨 **Multi-Channel Alerts**: Telegram, Discord, Slack, MS Teams, Webhooks, Email (SMTP), Desktop notifications, Audible alarms.
* 📄 **Incident Recording & PDF Reporting**: Instant screenshot capture, JSON metadata logging, CSV export, and automated PDF safety reports.
* 🌐 **FastAPI & Live Dashboard**: REST API (`/detect`, `/stream`, `/history`, `/health`, `/statistics`), WebSocket support, and modern glassmorphism web dashboard.
* 🔌 **Extensible Plugin Ecosystem**: SDK allowing custom third-party detectors with simple Python class inheritance.
* 💻 **Cross-Platform**: Supported on Windows, Linux, and macOS. Ready for Docker, Jetson, and Raspberry Pi deployments.

---

## 📦 Installation

```bash
pip install threatvision-ai
```

With optional deep learning backends:

```bash
pip install "threatvision-ai[ml]"
```

---

## 💻 Quick Start

```python
from threatvision import ThreatVision

tv = ThreatVision(
    camera=0,
    dashboard=True,
    save_incidents=True,
)

# Enable desired detection modules
tv.enable_person_detection()
tv.enable_weapon_detection()
tv.enable_fire_detection()
tv.enable_fight_detection()
tv.enable_smoke_detection()

# Start real-time analysis
tv.start()
```

Access the interactive command dashboard live at `http://127.0.0.1:8000`.

---

## ⚡ Command Line Interface (CLI)

ThreatVision AI includes a full-featured CLI:

```bash
# Run camera detection
threatvision camera --dashboard

# Process a video file
threatvision video movie.mp4

# Process an image file
threatvision image photo.jpg

# Launch standalone dashboard
threatvision dashboard --port 8000

# Run performance benchmark
threatvision benchmark -n 200

# Generate sample YAML config
threatvision config -o config.yaml
```

---

## 🔌 Custom Plugin Development

Create custom AI detectors with the ThreatVision Plugin SDK:

```python
from threatvision import Plugin, register_plugin, Detection, ThreatVision
import numpy as np

@register_plugin
class CustomSafetyGearDetector(Plugin):
    def detect(self, frame: np.ndarray):
        # Custom vision model / heuristic logic
        return [
            Detection(
                label="hardhat",
                confidence=0.95,
                box=(100, 100, 200, 200),
                category="safety"
            )
        ]

tv = ThreatVision(camera=0)
tv.add_custom_detector(CustomSafetyGearDetector("hardhat"))
```

---

## 🏗 Architecture

```
threatvision-ai/
├── threatvision/
│   ├── camera/        # Stream reader (webcam, RTSP, video, multi-camera)
│   ├── detectors/     # 11 Modular Detectors (Person, Weapon, Fire, etc.)
│   ├── tracking/      # Multi-object tracker, persistent IDs, heatmaps
│   ├── analytics/     # Threat scoring engine & spatial zone analytics
│   ├── alerts/        # Alert definitions
│   ├── notifications/ # Dispatcher (Telegram, Discord, Slack, Teams, Email)
│   ├── storage/       # Screenshot & JSON incident manager, CSV exporter
│   ├── reports/       # ReportLab PDF report exporter
│   ├── cloud/         # API client & cloud sync
│   ├── api/           # FastAPI REST & WebSocket streaming server
│   ├── dashboard/     # Modern web command center static assets
│   ├── plugins/       # Plugin SDK & registry
│   ├── cli/           # Click/Rich CLI suite
│   ├── config/        # YAML/TOML/JSON/Env settings manager
│   ├── logging/       # Rich structured logger
│   └── models/        # Model backends (YOLO, RT-DETR, ONNX, Fallback)
├── tests/             # Comprehensive Pytest suite (>95% coverage)
├── examples/          # Runnable developer scripts
├── benchmarks/        # Performance FPS benchmarking tool
├── Dockerfile & docker-compose.yml
└── pyproject.toml
```

---

## 🛡️ License & Ethics

Distributed under the **MIT License**. See `LICENSE` for more information.

ThreatVision AI is committed to open, safe, and transparent AI development. It must not be deployed for unlawful surveillance or autonomous weapon control.
