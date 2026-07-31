"""Unit tests for Multi-Object Tracker."""

import pytest
from threatvision.models.backend import Detection
from threatvision.tracking.tracker import Tracker

def test_tracker_registration_and_update():
    tracker = Tracker(max_disappeared=5)
    
    det1 = Detection(label="person", confidence=0.9, box=(10, 10, 50, 100))
    tracked1 = tracker.update([det1])
    
    assert len(tracker.tracked_objects) == 1
    t_id = tracked1[0].track_id
    assert t_id is not None

    # Frame 2: slightly moved box
    det2 = Detection(label="person", confidence=0.92, box=(12, 12, 52, 102))
    tracked2 = tracker.update([det2])
    assert tracked2[0].track_id == t_id

def test_tracker_summary():
    tracker = Tracker()
    det = Detection(label="car", confidence=0.85, box=(100, 100, 200, 200))
    tracker.update([det])
    
    summary = tracker.get_summary()
    assert summary["active_tracks"] == 1
    assert summary["total_entered"] == 1
