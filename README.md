# ThreatVision AI: Technical Architecture, Mathematical Foundations, and System Reference Manual

## Abstract

ThreatVision AI (`threatvision-ai`) is an open-source, modular computer vision framework designed for real-time threat detection, multi-object tracking, spatial analytics, and multi-channel incident response. Operating on streaming video input from live cameras, RTSP network streams, video files, or static images, the framework evaluates visual hazards and computes a calibrated threat score. ThreatVision AI is engineered as an operator assistance framework. Detections return explicit confidence bounds and threat score evaluations rather than absolute assertions, assisting human operators in physical security monitoring.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Computer Vision Background](#2-computer-vision-background)
3. [System Architecture](#3-system-architecture)
4. [Mathematical Foundations](#4-mathematical-foundations)
5. [Installation Guide](#5-installation-guide)
6. [Quick Start Guide](#6-quick-start-guide)
8. [Detection Modules Specification](#8-detection-modules-specification)
9. [Threat Scoring Engine & Risk Matrix](#9-threat-scoring-engine--risk-matrix)
10. [Web Dashboard & Command Center UI](#10-web-dashboard--command-center-ui)
11. [Cloud REST API & WebSocket Streaming Specification](#11-cloud-rest-api--websocket-streaming-specification)
12. [Python API Class Reference](#12-python-api-class-reference)
13. [Configuration Management](#13-configuration-management)
14. [Command Line Interface (CLI) Reference](#14-command-line-interface-cli-reference)
15. [Notification Channels](#15-notification-channels)
16. [Logging & Monitoring](#16-logging--monitoring)
17. [Performance Optimization & Hardware Acceleration](#17-performance-optimization--hardware-acceleration)
18. [Security, Data Privacy & Responsible AI](#18-security-data-privacy--responsible-ai)
19. [Custom Plugin Development Guide](#19-custom-plugin-development-guide)
20. [Testing & Verification Strategy](#20-testing--verification-strategy)
21. [Production Deployment Guide](#21-production-deployment-guide)
22. [Frequently Asked Questions (FAQ)](#22-frequently-asked-questions-faq)
23. [Troubleshooting Matrix](#23-troubleshooting-matrix)
24. [Version History & Changelog](#24-version-history--changelog)
25. [Future Development Roadmap](#25-future-development-roadmap)
26. [Comprehensive Technical & Domain Glossary](#26-comprehensive-technical--domain-glossary)

---

## 1. Introduction

### 1.1 What is ThreatVision AI?

ThreatVision AI is an open-source Python framework for building camera-based physical security monitoring systems. It provides a modular pipeline—camera ingestion, object detection, multi-object tracking, behavior analysis, threat scoring, and human review—that developers assemble into monitoring applications ranging from a single-webcam prototype to a multi-site, multi-thousand-camera deployment.

Rather than shipping a single monolithic "detect everything" model, ThreatVision AI composes specialized, independently maintained detectors (person, vehicle, weapon-shape, fire/smoke, fall, crowd density, and others) behind a common interface, and combines their outputs through a transparent, configurable scoring engine.

### 1.2 Why Was It Created?

Camera-based security monitoring at scale faces a structural bottleneck: a human operator can attentively watch only a handful of video feeds at once, and attention degrades quickly during long shifts on low-signal footage. Existing options in this space historically fell into two categories:

1. **Closed, proprietary appliances** — reliable but opaque, difficult to audit, and expensive to customize or extend.
2. **Research-grade computer vision code** — flexible and transparent, but requiring significant engineering investment to turn into a deployable monitoring system with tracking, scoring, review workflows, and notifications.

ThreatVision AI was created to sit between these: a package that gives engineering teams inspectable, extensible building blocks while providing the operational scaffolding (dashboard, API, notifications, deployment tooling) needed to run a monitoring system in production.

### 1.3 Problems It Solves

| Problem | How ThreatVision AI Addresses It |
| :--- | :--- |
| Operators cannot watch every feed at all times | Automated detection surfaces candidate events for review rather than requiring continuous manual attention. |
| Raw model output is hard to act on | The threat scoring engine converts per-frame detections into zone- and time-aware incident scores. |
| Alert fatigue from high false-positive rates | Temporal persistence checks, zone rules, and confidence thresholds are combined and tunable per deployment. |
| Vendor lock-in and opaque decision logic | Fully open pipeline; every stage from detection to scoring is inspectable and replaceable. |
| Disconnected tooling | Single framework covering ingestion through notification, with a plugin system for custom components. |
| Difficult evaluation of detector quality | Built-in benchmarking, confusion-matrix, and PR-curve tooling. |

### 1.4 Goals & Principles

- **Transparency** — Every detection and score must be traceable to the model, frame, and rule that produced it.
- **Human-in-the-loop by default** — Surfacing information for human decision-making, not automating force or legal actions.
- **Composability** — Detectors, trackers, scorers, and notifiers are independently swappable.
- **Operational Realism** — Addresses the full lifecycle (deployment, logging, monitoring, performance tuning), not just model inference.
- **Honesty about limitations** — Documentation and defaults make failure modes and confidence limits visible rather than overstating reliability.

---

## 2. Computer Vision Background

### 2.1 AI, Machine Learning, and Deep Learning Hierarchy

```text
Artificial Intelligence (AI)
└── Machine Learning (ML)
    └── Deep Learning (DL)
        ├── Convolutional Neural Networks (CNNs for spatial features)
        └── Vision Transformers (ViT for attention-based models)
```

Deep networks learn a hierarchy of representations: early layers respond to edges and textures, middle layers to parts (hand, blade shape), and later layers to whole objects. This hierarchy allows transfer learning across ThreatVision AI's different detectors.

### 2.2 Core Computer Vision Tasks

| Task | Core Question | ThreatVision AI Usage |
| :--- | :--- | :--- |
| Image Classification | "What is in this image?" | Scene-level checks (indoor/outdoor) |
| Object Detection | "What objects are here, and where?" | Bounding box localization for person, vehicle, weapon-shape, fire/smoke |
| Multi-Object Tracking | "Which object is the same across frames?" | Track persistence, trajectory analysis, loitering, and dwell time |
| Pose Estimation | "How is this person's body positioned?" | Keypoint estimation for fall and fight detection |
| Action Recognition | "What is happening over time?" | Temporal activity recognition (falling, fighting, motion energy) |

### 2.3 Object Detection Architectures

1. **Single-stage detectors (e.g., YOLO series)** — Predict bounding boxes and class probabilities directly in a single forward pass. Faster, used for real-time streaming pipeline.
2. **Two-stage detectors (e.g., Faster R-CNN)** — Propose candidate regions first, then classify each region. Higher accuracy, used for offline re-verification of borderline incidents.

---

## 3. System Architecture

### 3.1 High-Level Pipeline Architecture

```text
Camera Sources (Webcam / RTSP / Video File / Cloud Stream)
                        │
                        ▼
           [Ingestion & Preprocessing Layer]
            (Async Frame Decoding & Resizing)
                        │
                        ▼
           [Modular Detection Pipeline]
       (Person, Weapon, Fire, Smoke, etc.)
                        │
                        ▼
           [Multi-Object Tracking Layer]
      (Kalman Filter + Data Association)
                        │
                        ▼
           [Threat Scoring & Fusion Engine]
     (Weights, Zone Multipliers, Persistence)
                        │
                        ▼
           [Human Review & Alert Dispatch]
            /           │           \
           ▼            ▼            ▼
      [Dashboard]  [Cloud API]  [Notifications]
```

### 3.2 Detailed Data Flow Lifecycle

1. **Ingestion**: Reads raw frames from input stream at specified frame rate.
2. **Preprocessing**: Resizes frames, normalizes color space, and applies optional frame-skipping.
3. **Detection**: Runs active detectors in parallel, yielding raw `Detection` objects.
4. **Tracking**: Assigns persistent track IDs and computes movement vectors.
5. **Scoring**: Fuses detections, class severity, zone weights, and persistence into a single threat score $S \in [0, 1]$.
6. **Review Queue**: Routes incidents above threshold to human review.
7. **Action**: Dispatches alerts to Telegram, Discord, Slack, Webhooks, or REST endpoints upon confirmation.

---

## 4. Mathematical Foundations

### 4.1 Intersection over Union (IoU)

Given two bounding boxes $A = (x_{A1}, y_{A1}, x_{A2}, y_{A2})$ and $B = (x_{B1}, y_{B1}, x_{B2}, y_{B2})$:

$$\text{Area}(A) = (x_{A2} - x_{A1}) \times (y_{A2} - y_{A1})$$

$$\text{Area}(B) = (x_{B2} - x_{B1}) \times (y_{B2} - y_{B1})$$

$$I(A, B) = \max(0, \min(x_{A2}, x_{B2}) - \max(x_{A1}, x_{B1})) \times \max(0, \min(y_{A2}, y_{B2}) - \max(y_{A1}, y_{B1}))$$

$$\text{IoU}(A, B) = \frac{I(A, B)}{\text{Area}(A) + \text{Area}(B) - I(A, B)}$$

*Numerical Example*: Box $A = [0, 0, 10, 10]$ ($\text{Area} = 100$), Box $B = [5, 5, 15, 15]$ ($\text{Area} = 100$). Intersection is $[5, 5, 10, 10]$ ($\text{Area} = 25$). Union is $100 + 100 - 25 = 175$.

$$\text{IoU} = \frac{25}{175} \approx 0.143$$

### 4.2 Precision, Recall, and F1 Score

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

*Numerical Example*: $\text{TP} = 80, \text{FP} = 20, \text{FN} = 10 \implies \text{Precision} = \frac{80}{100} = 0.80$, $\text{Recall} = \frac{80}{90} \approx 0.889$, $\text{F1} \approx 0.842$.

### 4.3 Mean Average Precision (mAP)

$$\text{mAP} = \frac{1}{N} \sum_{i=1}^N \text{AP}_i$$

Where $\text{AP}_i$ is the area under the Precision-Recall curve for class $i$. Evaluated at $\text{mAP}@0.5$ and $\text{mAP}@[0.5:0.95]$.

### 4.4 Non-Maximum Suppression (NMS)

Sort detections $D$ by confidence descending. Select box $b_{max}$ with highest confidence, add to kept set $K$, and discard any box $b \in D$ where $\text{IoU}(b_{max}, b) > \tau_{\text{NMS}}$ (default $\tau_{\text{NMS}} = 0.45$).

### 4.5 Activation Functions: Sigmoid and Softmax

$$\text{Sigmoid}(x) = \frac{1}{1 + e^{-x}}$$

$$\text{Softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}}$$

### 4.6 Loss Functions: Cross-Entropy

- **Binary Cross-Entropy (BCE)**:

$$\mathcal{L}_{\text{BCE}} = - [y \log(p) + (1 - y) \log(1 - p)]$$

- **Categorical Cross-Entropy (CCE)**:

$$\mathcal{L}_{\text{CCE}} = - \sum_{c=1}^C y_c \log(p_c)$$

### 4.7 Kalman Filter Tracking Formulation

State vector $\mathbf{x}_k = [x, y, v_x, v_y]^T$.

- **Predict Step**:

$$\mathbf{\hat{x}}_k = \mathbf{F} \mathbf{x}_{k-1}$$

$$\mathbf{P}_k = \mathbf{F} \mathbf{P}_{k-1} \mathbf{F}^T + \mathbf{Q}$$

- **Update Step**:

$$\mathbf{K}_k = \mathbf{P}_k \mathbf{H}^T (\mathbf{H} \mathbf{P}_k \mathbf{H}^T + \mathbf{R})^{-1}$$

$$\mathbf{x}_k = \mathbf{\hat{x}}_k + \mathbf{K}_k (\mathbf{z}_k - \mathbf{H} \mathbf{\hat{x}}_k)$$

$$\mathbf{P}_k = (\mathbf{I} - \mathbf{K}_k \mathbf{H}) \mathbf{P}_k$$

### 4.8 Distance Metrics & Data Association

- **Cosine Similarity**:

$$\text{sim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$

- **Euclidean Distance**:

$$d(\mathbf{u}, \mathbf{v}) = \sqrt{\sum_{i=1}^n (u_i - v_i)^2}$$

- **Association Cost Matrix**:

$$\mathbf{C}_{i,j} = \alpha (1 - \text{IoU}_{i,j}) + (1 - \alpha)(1 - \text{sim}_{i,j})$$

---

## 5. Installation Guide

### 5.1 Package Installation

```bash
# Core CPU installation
pip install threatvision-ai

# Installation with GPU acceleration (PyTorch CUDA / ONNX Runtime GPU)
pip install "threatvision-ai[gpu]"
```

### 5.2 Local Source Setup

```bash
git clone https://github.com/Amit123103/multithread_detection.git
cd multithread_detection
pip install -e ".[dev]"
```

### 5.3 Containerized Execution (Docker)

```bash
docker build -t threatvision:latest .
docker run --gpus all -p 8000:8000 threatvision:latest
```

---

## 6. Quick Start Guide

```python
from threatvision import ThreatVision

# Initialize security engine
tv = ThreatVision(camera=0, dashboard=True, save_incidents=True)

# Enable active threat detectors
tv.enable_person_detection(threshold=0.5)
tv.enable_weapon_detection(threshold=0.6)
tv.enable_fire_detection(threshold=0.55)
tv.enable_fight_detection(threshold=0.6)
tv.enable_smoke_detection(threshold=0.55)

# Start real-time analysis pipeline
tv.start(block=True)
```

---

## 8. Detection Modules Specification

ThreatVision AI features 11 specialized detection modules:

1. **Person Detector** — Human detection baseline for behavior analysis.
2. **Weapon Detector** — Identifies visual patterns for handguns, rifles, and knives.
3. **Fire Detector** — Detects open flames via HSV color analytics and deep model inference.
4. **Smoke Detector** — Detects smoke plumes via chrominance and contrast analysis.
5. **Vehicle Detector** — Detects cars, trucks, buses, and motorcycles.
6. **Accident Detector** — Identifies vehicle collisions using bounding box IoU dynamics.
7. **Fight Detector** — Flags physical altercations based on high-energy overlapping person bounding boxes.
8. **Fall Detector** — Detects human falls when bounding box aspect ratio $\text{AR} = \frac{w}{h} > 1.25$.
9. **Intrusion Detector** — Flags ray-casting point-in-polygon entry into restricted perimeter zones.
10. **Crowd Detector** — Triggers density alerts when person counts in a region exceed threshold.
11. **Package Detector** — Detects unattended backpacks, suitcases, and parcels.

---

## 9. Threat Scoring Engine & Risk Matrix

### 9.1 Threat Score Formula

$$S = \min\left(1.0, \, w_1 C + w_2 W_{\text{class}} + w_3 W_{\text{zone}} + w_4 F_{\text{persist}}\right)$$

Where $C$ is model confidence, $W_{\text{class}}$ is class severity, $W_{\text{zone}}$ is zone multiplier, $F_{\text{persist}}$ is temporal persistence factor, and $w_1=0.4, w_2=0.3, w_3=0.2, w_4=0.1$.

### 9.2 Risk Category Mapping

$$L(S) = \begin{cases}
\text{CRITICAL}, & S \ge 0.85 \\
\text{HIGH}, & 0.60 \le S < 0.85 \\
\text{MEDIUM}, & 0.30 \le S < 0.60 \\
\text{LOW}, & 0.15 \le S < 0.30 \\
\text{SAFE}, & S < 0.15
\end{cases}$$

---

## 10. Web Dashboard & Command Center UI

The Web Dashboard runs on FastAPI and HTML5/JS:

- **Live Grid View**: Real-time camera feed rendering with overlay HUD.
- **Incident Timeline**: Filterable event log with threat scores and screenshots.
- **Telemetry Statistics**: FPS, memory usage, CPU/GPU utilization charts.
- **Review Queue**: Confirmation controls for human operators.

---

## 11. Cloud REST API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health status |
| `GET` | `/statistics` | FPS, threat telemetry, CPU/RAM utilization |
| `POST` | `/detect` | Upload frame for detection JSON payload |
| `GET` | `/history` | Fetch incident log history |
| `GET` | `/history/csv` | Download incident log as CSV |
| `GET` | `/stream` | Live video MJPEG stream |

---

## 12. Python API Reference

```python
from threatvision import ThreatVision, ThreatVisionConfig

config = ThreatVisionConfig()
tv = ThreatVision(camera=0, config=config)
tv.enable_person_detection(threshold=0.5)
tv.enable_weapon_detection(threshold=0.6)
tv.start(block=False)

stats = tv.get_statistics()
print(stats)
```

---

## 13. Configuration Management

Configurations can be loaded from YAML, TOML, or JSON:

```yaml
camera:
  width: 1280
  height: 720
  skip_frames: 0

analytics:
  threat_threshold_low: 0.25
  threat_threshold_high: 0.75

notifications:
  enable_webhook: false
```

---

## 14. Command Line Interface (CLI)

```bash
# Run camera stream with web dashboard
threatvision camera --source 0 --port 8000

# Run offline video file evaluation
threatvision video sample.mp4

# Run single image evaluation
threatvision image frame.jpg

# Launch standalone dashboard server
threatvision dashboard --host 127.0.0.1 --port 8000

# Run benchmark test
threatvision benchmark --frames 100
```

---

## 15. Notification Channels

ThreatVision AI dispatches alerts to multiple destinations:
- **Telegram Bot**: API token & chat ID integration.
- **Discord Webhook**: Embedded alert messages with threat score details.
- **Slack Webhook**: Custom channel alert payloads.
- **Generic HTTP Webhook**: JSON payloads for integration with SIEMs.
- **Audible Local Alarm**: System alert beep on CRITICAL severity.

---

## 16. Logging & Monitoring

- **Structured JSON Logs**: Machine-readable logs for ELK / Loki pipelines.
- **Performance Monitor**: FPS and inference latency metrics via `PerformanceMonitor`.

---

## 17. Performance Optimization

- **GPU Acceleration**: PyTorch CUDA and ONNX Runtime GPU support.
- **Frame Skipping**: Skip non-critical frames to optimize multi-camera throughput.
- **Quantization**: INT8 quantization support for edge devices.

---

## 18. Security & Responsible AI

- **Human-in-the-Loop**: High-severity automated actions require operator review by default.
- **Data Minimization**: Only metadata and short incident clips are logged.
- **No Autonomous Weapon Integration**: Strictly designed for monitoring and alerting.

---

## 19. Custom Plugin Development Guide

```python
from threatvision import Plugin, register_plugin, Detection
import numpy as np

@register_plugin
class ThermalDetector(Plugin):
    def __init__(self):
        super().__init__(name="thermal")

    def detect(self, frame: np.ndarray):
        return [
            Detection(label="hotspot", confidence=0.88, box=(50, 50, 150, 150), category="thermal")
        ]
```

---

## 20. Testing & Verification

The suite contains 32 automated tests:

```text
pytest -o addopts=""
32 passed in 5.89s
```

---

## 21. Production Deployment Guide

### Linux Systemd Service

```ini
[Unit]
Description=ThreatVision AI Service
After=network.target

[Service]
ExecStart=/usr/local/bin/threatvision camera --source 0
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 22. Frequently Asked Questions (FAQ)

- **Q: Is GPU required?**
  *A: No, CPU inference with synthetic/ONNX fallback is supported out of the box.*
- **Q: Does ThreatVision AI perform facial recognition?**
  *A: No. ThreatVision AI tracks object shapes and bounding boxes, not personal biometric identities.*

---

## 23. Troubleshooting Matrix

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Camera fails to open | Wrong index or RTSP URL | Verify camera index or test RTSP URL in VLC/ffprobe |
| Low FPS | High frame resolution or CPU bound | Enable frame skipping or use ONNX/CUDA backend |
| Missing `python-multipart` error | Form parser dependency missing | Run `pip install python-multipart` |

---

## 24. Changelog

- **v2.4.1**: Complete CI/CD fixes, Ruff import sorting, Mypy type annotation fixes, `python-multipart` integration, and full academic manual documentation.
- **v1.0.0**: Initial release with person, vehicle, and weapon detection modules.

---

## 25. Roadmap

- **Near-term**: Multi-camera cross-view tracking and adaptive thresholding.
- **Long-term**: Edge device optimization for Jetson Orin and Raspberry Pi 5.

---

## 26. Comprehensive Technical & Domain Glossary

- **IoU (Intersection over Union)**: Ratio of bounding box intersection area to union area.
- **NMS (Non-Maximum Suppression)**: Post-processing step eliminating overlapping bounding box proposals.
- **Kalman Filter**: Recursive state estimation algorithm predicting object trajectory across frames.
- **Threat Score**: Calibrated scalar metric $S \in [0, 1]$ representing hazard severity.

---

## License

ThreatVision AI is released under the **MIT License**.
