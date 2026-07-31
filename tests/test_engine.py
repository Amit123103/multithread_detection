"""Unit tests for main ThreatVision core engine."""

import numpy as np

from threatvision.engine import ThreatVision


def test_engine_initialization():
    tv = ThreatVision(camera=0)
    assert not tv.is_running
    assert len(tv.detectors) == 0


def test_engine_enable_detectors():
    tv = ThreatVision(camera=0)
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()

    assert "person" in tv.detectors
    assert "weapon" in tv.detectors
    assert "fire" in tv.detectors


def test_process_single_frame():
    tv = ThreatVision(camera=0)
    tv.enable_person_detection()

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    eval_result, detections = tv.process_single_frame(dummy_frame)

    assert eval_result is not None
    assert isinstance(detections, list)
