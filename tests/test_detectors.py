"""Unit tests for all ThreatVision detectors."""

import numpy as np
import pytest

from threatvision.detectors.accident import AccidentDetector
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


@pytest.fixture
def dummy_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


def test_person_detector(dummy_frame):
    detector = PersonDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)
    for d in detections:
        assert d.category == "person"


def test_weapon_detector(dummy_frame):
    detector = WeaponDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_fire_detector(dummy_frame):
    detector = FireDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_smoke_detector(dummy_frame):
    detector = SmokeDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_vehicle_detector(dummy_frame):
    detector = VehicleDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_accident_detector(dummy_frame):
    detector = AccidentDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_fight_detector(dummy_frame):
    detector = FightDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_fall_detector(dummy_frame):
    detector = FallDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_intrusion_detector(dummy_frame):
    poly = [(10, 10), (300, 10), (300, 300), (10, 300)]
    detector = IntrusionDetector(restricted_polygons=[poly])
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_crowd_detector(dummy_frame):
    detector = CrowdDetector(density_threshold=1)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)


def test_package_detector(dummy_frame):
    detector = PackageDetector(confidence_threshold=0.5)
    detections = detector.detect(dummy_frame)
    assert isinstance(detections, list)
