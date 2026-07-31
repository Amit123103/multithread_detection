# ThreatVision AI: Technical Architecture and System Specification Report

## Abstract

ThreatVision AI (`threatvision-ai`) is an open-source, modular computer vision framework designed for real-time threat detection, multi-object tracking, spatial analytics, and multi-channel incident response. Operating on streaming video input from live cameras, RTSP network streams, video files, or static images, the framework evaluates visual hazards and computes a calibrated threat score. ThreatVision AI is engineered as an operator assistance framework. Detections return explicit confidence bounds and threat score evaluations rather than absolute assertions, assisting human operators in monitoring visual environments.

---

## 1. System Architecture

ThreatVision AI follows a decoupled, clean architecture comprising six primary subsystems: Input Ingestion, Detection Engine, Object Tracking & Spatial Analytics, Threat Scoring Engine, Incident Storage & Alert Dispatching, and Presentation (REST API & Dashboard).

```
                      +-----------------------------+
                      |     Input Video Sources     |
                      | (Webcam / RTSP / File / Img)|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Camera Ingestion Thread  |
                      |   (Async Frame Buffer)      |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Base Detector SDK        |
                      | (YOLO / ONNX / Heuristic)   |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Multi-Object Tracker     |
                      |   (IoU Data Association)    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Threat Scoring Engine    |
                      | (Fusion & Threat Level Math)|
                      +--------------+--------------+
                                     |
            +------------------------+------------------------+
            |                                                 |
            v                                                 v
+-----------------------+                         +-----------------------+
| Incident Storage &    |                         | FastAPI Cloud Server  |
| Report Generation     |                         | & Live Web Dashboard  |
| (JSON / CSV / PDF)    |                         | (REST / MJPEG Stream) |
+-----------------------+                         +-----------------------+
```

---

## 2. Mathematical Formulations and Analytics

### 2.1 Bounding Box Representation and Centroid Computation

A bounding box $d$ is defined by top-left coordinate $(x_1, y_1)$ and bottom-right coordinate $(x_2, y_2)$:

$$d = (x_1, y_1, x_2, y_2) \quad \text{where } x_1 < x_2, \, y_1 < y_2$$

The spatial centroid $(c_x, c_y)$ of bounding box $d$ is calculated as:

$$c_x = \left\lfloor \frac{x_1 + x_2}{2} \right\rfloor, \quad c_y = \left\lfloor \frac{y_1 + y_2}{2} \right\rfloor$$

---

### 2.2 Spatial Overlap via Intersection over Union (IoU)

For two bounding boxes $A = (x_{A1}, y_{A1}, x_{A2}, y_{A2})$ and $B = (x_{B1}, y_{B1}, x_{B2}, y_{B2})$, the intersection area $I(A, B)$ and union area $U(A, B)$ are computed as:

$$x_{\text{inter1}} = \max(x_{A1}, x_{B1}), \quad y_{\text{inter1}} = \max(y_{A1}, y_{B1})$$
$$x_{\text{inter2}} = \min(x_{A2}, x_{B2}), \quad y_{\text{inter2}} = \min(y_{A2}, y_{B2})$$

$$I(A, B) = \max(0, x_{\text{inter2}} - x_{\text{inter1}} + 1) \times \max(0, y_{\text{inter2}} - y_{\text{inter1}} + 1)$$

$$\text{Area}(A) = (x_{A2} - x_{A1} + 1) \times (y_{A2} - y_{A1} + 1)$$
$$\text{Area}(B) = (x_{B2} - x_{B1} + 1) \times (y_{B2} - y_{B1} + 1)$$

$$\text{IoU}(A, B) = \frac{I(A, B)}{\text{Area}(A) + \text{Area}(B) - I(A, B)}$$

IoU is utilized in collision detection, fight proximity evaluation, and object tracking data association.

---

### 2.3 Ray-Casting Point-in-Polygon Test for Zone Intrusion

To determine whether a object centroid $P(x, y)$ resides inside a restricted perimeter polygon defined by vertices $V = [(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)]$, ray-casting checks horizontal ray intersections. For edge segment $(V_i, V_j)$ where $V_j = V_{(i \bmod n) + 1}$:

$$\text{if } \left(y > \min(y_i, y_j)\right) \land \left(y \le \max(y_i, y_j)\right) \land \left(x \le \max(x_i, x_j)\right):$$

$$x_{\text{intersection}} = \frac{(y - y_i)(x_j - x_i)}{y_j - y_i} + x_i$$

If $x \le x_{\text{intersection}}$, the ray intersection state toggles. An odd number of total intersections confirms spatial intrusion ($P \in \text{Polygon}$).

---

### 2.4 Multi-Detector Threat Fusion Matrix

Each detection $d_i$ possesses a model confidence $\gamma_i \in [0, 1]$ and an assigned category weight $w(c_i) \in [0, 1]$:

| Category ($c_i$) | Inherent Hazard Weight $w(c_i)$ |
| :--- | :--- |
| Weapon (Gun, Rifle, Knife) | 0.95 |
| Fire | 0.90 |
| Fight / Violence | 0.85 |
| Vehicle Crash / Accident | 0.80 |
| Intrusion | 0.75 |
| Smoke | 0.70 |
| Fall / Lying Down | 0.65 |
| Unattended Package | 0.60 |
| Crowd Panic / Density | 0.50 |
| Vehicle | 0.15 |
| Person | 0.10 |

The unweighted hazard metric $S_i$ for detection $d_i$ is:

$$S_i = \gamma_i \times w(c_i)$$

The baseline frame threat score $S_{\text{base}}$ corresponds to the maximum single detection threat:

$$S_{\text{base}} = \max_{i=1 \dots K} S_i$$

Let $T = \{ d_i \mid S_i \ge \tau_{\text{low}} \}$ be the set of active triggering threats, where $\tau_{\text{low}} = 0.25$. To account for multi-threat compounding, the final threat score $S_{\text{final}}$ is evaluated as:

$$S_{\text{final}} = \min\left(1.0, \, S_{\text{base}} + \min\left(0.15, \, 0.05 \times (|T| - 1)\right)\right)$$

---

### 2.5 Threat Level Classification

The frame threat level $L(S_{\text{final}})$ is mapped via threshold intervals:

$$L(S) = \begin{cases}
\text{CRITICAL}, & S \ge 0.90 \\
\text{HIGH}, & 0.75 \le S < 0.90 \\
\text{MEDIUM}, & 0.50 \le S < 0.75 \\
\text{LOW}, & 0.25 \le S < 0.50 \\
\text{SAFE}, & S < 0.25
\end{cases}$$

---

### 2.6 Posture Aspect Ratio Analysis (Fall Detection)

For a detected person with bounding box dimensions width $w = x_2 - x_1$ and height $h = y_2 - y_1$:

$$\text{AR} = \frac{w}{h}$$

When $\text{AR} > 1.25$, the subject is classified in a horizontal posture, triggering a fall alert.

---

### 2.7 Multi-Object Tracking Data Association and Dwell Time

Tracks $T_k$ are paired with frame detections $D_j$ by constructing an IoU cost matrix $C_{k, j} = \text{IoU}(T_k, D_j)$. Matches satisfying $C_{k, j} \ge 0.30$ update track coordinates.

Track dwell time $t_{\text{dwell}}$ is measured as:

$$t_{\text{dwell}} = t_{\text{last\_seen}} - t_{\text{first\_seen}}$$

Loitering alerts trigger when $t_{\text{dwell}} \ge \tau_{\text{loiter}}$.

---

### 2.8 Throughput and Latency Formulation

For $N$ processed video frames with individual frame processing times $\Delta t_k$ and model inference times $t_{\text{inf}, k}$:

$$\text{FPS} = \frac{N}{\sum_{k=1}^N \Delta t_k}$$

$$\bar{L}_{\text{latency}} = \frac{1000}{N} \sum_{k=1}^N t_{\text{inf}, k} \quad (\text{ms})$$

---

## 3. Package Structure

```
threatvision-ai/
├── threatvision/
│   ├── __init__.py           # Package exports (ThreatVision, ThreatLevel, etc.)
│   ├── engine.py             # Core ThreatVision manager
│   ├── camera/
│   │   ├── stream.py         # Threaded camera, RTSP, video reader
│   │   └── __init__.py
│   ├── detectors/            # 11 Specialized Detectors
│   │   ├── base.py           # BaseDetector abstraction
│   │   ├── person.py         # Person detector
│   │   ├── weapon.py         # Gun, rifle, knife detector
│   │   ├── fire.py           # Fire detector
│   │   ├── smoke.py          # Smoke hazard detector
│   │   ├── vehicle.py        # Vehicle classifier
│   │   ├── accident.py       # Collision detector
│   │   ├── fight.py          # Violence detector
│   │   ├── fall.py           # Fall & lying down detector
│   │   ├── intrusion.py      # Zone intrusion detector
│   │   ├── crowd.py          # Crowd density detector
│   │   └── package.py        # Unattended package detector
│   ├── models/
│   │   └── backend.py        # Model loaders (YOLO, RT-DETR, ONNX, Fallback)
│   ├── tracking/
│   │   └── tracker.py        # Centroid/IoU multi-object tracker
│   ├── analytics/
│   │   ├── threat_engine.py  # Threat score & fusion math
│   │   └── spatial.py        # Perimeter zones & loitering analytics
│   ├── storage/
│   │   └── incident_manager.py # JSON/CSV log storage & screenshot capture
│   ├── reports/
│   │   └── pdf_exporter.py   # ReportLab PDF report generation
│   ├── alerts/
│   │   └── alert_types.py    # Alert message models
│   ├── notifications/
│   │   └── dispatcher.py     # Telegram, Discord, Slack, Teams, Email dispatcher
│   ├── cloud/                # REST API client
│   ├── api/
│   │   └── app.py            # FastAPI REST & WebSocket streaming server
│   ├── dashboard/            # Static HTML5/CSS3/JS Web UI
│   ├── plugins/
│   │   └── plugin.py         # Plugin SDK & registry
│   ├── cli/
│   │   └── cli.py            # Command Line Interface suite
│   ├── config/
│   │   └── config.py         # YAML/TOML/JSON/Env settings manager
│   ├── logging/
│   │   └── logger.py         # Rich structured logging
│   └── utils/
│       ├── draw.py           # HUD & bounding box rendering
│       ├── geometry.py       # Spatial math utilities
│       └── metrics.py        # Performance & resource monitor
├── tests/                    # 9 Test Suites (32 Unit Tests)
├── examples/                 # Runnable python scripts
├── benchmarks/               # Performance benchmark script
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 4. Installation and Setup

### 4.1 PyPI Package Installation

```bash
pip install threatvision-ai
```

### 4.2 Installation with Machine Learning Dependencies

```bash
pip install "threatvision-ai[ml]"
```

### 4.3 Local Development Setup

```bash
git clone https://github.com/Amit123103/multithread_detection.git
cd multithread_detection
pip install -e ".[dev]"
```

---

## 5. Python API Usage

```python
from threatvision import ThreatVision

# Initialize engine on default camera input
tv = ThreatVision(
    camera=0,
    dashboard=True,
    save_incidents=True,
)

# Enable active detectors
tv.enable_person_detection(threshold=0.5)
tv.enable_weapon_detection(threshold=0.6)
tv.enable_fire_detection(threshold=0.55)
tv.enable_fight_detection(threshold=0.6)
tv.enable_smoke_detection(threshold=0.55)

# Start threat analysis engine
tv.start()
```

---

## 6. Command Line Interface Reference

ThreatVision AI includes a command line interface (`threatvision`):

| Command | Usage | Description |
| :--- | :--- | :--- |
| `threatvision camera` | `threatvision camera -s 0 --dashboard` | Stream live threat detection from camera source |
| `threatvision video` | `threatvision video sample.mp4` | Process offline video file |
| `threatvision image` | `threatvision image frame.jpg` | Process single image and print detailed telemetry |
| `threatvision dashboard`| `threatvision dashboard --port 8000` | Launch standalone FastAPI backend and Web UI |
| `threatvision benchmark`| `threatvision benchmark -n 200` | Run throughput (FPS) and latency benchmark |
| `threatvision config` | `threatvision config -o config.yaml` | Export default configuration YAML file |

---

## 7. Cloud REST API Specification

FastAPI powers the cloud API server. Automatically generated documentation is accessible at `/docs` and `/redoc`.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health status and engine state |
| `GET` | `/statistics` | Real-time FPS, threat score, active count, CPU/RAM utilization |
| `POST` | `/detect` | Upload single image frame and receive detection JSON payload |
| `GET` | `/history` | Fetch security incident history logs |
| `GET` | `/history/csv` | Download incident history log as CSV file |
| `GET` | `/stream` | Live video feed stream (multipart/x-mixed-replace MJPEG) |

---

## 8. Custom Plugin SDK

Developers can extend ThreatVision AI by inheriting from the `Plugin` class:

```python
from threatvision import Plugin, register_plugin, Detection, ThreatVision
import numpy as np

@register_plugin
class HardHatDetector(Plugin):
    def __init__(self):
        super().__init__(name="hardhat")

    def detect(self, frame: np.ndarray):
        # Custom visual processing or model inference logic
        return [
            Detection(
                label="hardhat",
                confidence=0.92,
                box=(100, 100, 200, 200),
                category="safety_gear"
            )
        ]

tv = ThreatVision(camera=0)
tv.add_custom_detector(HardHatDetector())
```

---

## 9. Verification and Test Results

The test suite comprises 32 automated unit tests across 9 test modules:

```text
tests/test_api.py ..................... [PASS]
tests/test_cli.py ..................... [PASS]
tests/test_config.py .................. [PASS]
tests/test_detectors.py ............... [PASS]
tests/test_engine.py .................. [PASS]
tests/test_plugins.py ................. [PASS]
tests/test_storage.py ................. [PASS]
tests/test_threat_engine.py ........... [PASS]
tests/test_tracking.py ................ [PASS]

Result: 32 passed in 6.23s (100% Pass Rate)
```

---

## 10. License and Safety Statement

ThreatVision AI is released under the **MIT License**.

**Safety Operational Mandate**: ThreatVision AI is engineered exclusively to assist human operators in monitoring visual safety environments. Detections represent calibrated confidence outputs and threat score assessments. The framework must not be used for autonomous force application, critical decision automation without human oversight, or unlawful surveillance.
