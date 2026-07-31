# Quickstart Guide

Getting started with ThreatVision AI in under 2 minutes.

## 1. Installation

```bash
pip install threatvision-ai
```

## 2. Basic Python Example

```python
from threatvision import ThreatVision

tv = ThreatVision(
    camera=0,
    dashboard=True,
    save_incidents=True,
)

tv.enable_person_detection()
tv.enable_weapon_detection()
tv.enable_fire_detection()
tv.enable_fight_detection()

tv.start()
```

Navigate to `http://127.0.0.1:8000` to view the live dashboard.

## 3. Command Line Usage

Run live camera detection directly from your shell:

```bash
threatvision camera --dashboard
```

Process a video file:

```bash
threatvision video movie.mp4
```

Analyze a single picture:

```bash
threatvision image photo.jpg
```
