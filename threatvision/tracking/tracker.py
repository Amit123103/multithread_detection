"""Multi-object tracking engine with persistent IDs, trajectories, heatmaps, and entry/exit counters."""

import time
from typing import Dict, List, Tuple
import numpy as np
from threatvision.models.backend import Detection
from threatvision.utils.geometry import box_centroid, compute_iou


class TrackedObject:
    """Represents a single tracked target across video frames."""

    def __init__(self, track_id: int, initial_detection: Detection):
        self.track_id = track_id
        self.label = initial_detection.label
        self.category = initial_detection.category
        self.box = initial_detection.box
        self.confidence = initial_detection.confidence

        self.first_seen = time.time()
        self.last_seen = time.time()
        self.disappeared_frames = 0

        self.trajectory: List[Tuple[int, int]] = [box_centroid(initial_detection.box)]

    def update(self, detection: Detection) -> None:
        self.box = detection.box
        self.confidence = detection.confidence
        self.last_seen = time.time()
        self.disappeared_frames = 0
        self.trajectory.append(box_centroid(detection.box))

    @property
    def dwell_time_seconds(self) -> float:
        return self.last_seen - self.first_seen


class Tracker:
    """Centroid & IoU-based multi-object tracker supporting heatmaps and counting."""

    def __init__(self, max_disappeared: int = 15, iou_threshold: float = 0.3):
        self.next_track_id = 1
        self.tracked_objects: Dict[int, TrackedObject] = {}
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold

        self.total_entered = 0
        self.total_exited = 0
        self.heatmap: np.ndarray | None = None

    def update(
        self, detections: List[Detection], frame_shape: Tuple[int, int] | None = None
    ) -> List[Detection]:
        """Update tracks with new frame detections and attach track_ids."""
        if frame_shape and self.heatmap is None:
            self.heatmap = np.zeros(frame_shape, dtype=np.float32)

        # Update spatial heatmap
        if self.heatmap is not None:
            for det in detections:
                cx, cy = box_centroid(det.box)
                if 0 <= cy < self.heatmap.shape[0] and 0 <= cx < self.heatmap.shape[1]:
                    self.heatmap[cy, cx] += 1.0

        if not self.tracked_objects:
            # Register all initial detections
            for det in detections:
                self._register(det)
            return self._get_updated_detections(detections)

        # Pair existing tracks with new detections using IoU matrix
        track_ids = list(self.tracked_objects.keys())
        updated_detection_map: Dict[int, Detection] = {}

        matched_det_indices = set()
        for t_id in track_ids:
            track = self.tracked_objects[t_id]
            best_iou = 0.0
            best_det_idx = -1

            for idx, det in enumerate(detections):
                if idx in matched_det_indices:
                    continue
                iou = compute_iou(track.box, det.box)
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_det_idx = idx

            if best_det_idx != -1:
                matched_det_indices.add(best_det_idx)
                track.update(detections[best_det_idx])
                updated_detection_map[best_det_idx] = detections[best_det_idx]
                detections[best_det_idx].track_id = t_id
            else:
                track.disappeared_frames += 1

        # Register un-matched new detections
        for idx, det in enumerate(detections):
            if idx not in matched_det_indices:
                t_id = self._register(det)
                det.track_id = t_id

        # Purge stale tracks exceeding max_disappeared
        stale_ids = [
            t_id
            for t_id, track in self.tracked_objects.items()
            if track.disappeared_frames > self.max_disappeared
        ]
        for t_id in stale_ids:
            self.total_exited += 1
            del self.tracked_objects[t_id]

        return detections

    def _register(self, detection: Detection) -> int:
        t_id = self.next_track_id
        self.tracked_objects[t_id] = TrackedObject(t_id, detection)
        self.next_track_id += 1
        self.total_entered += 1
        return t_id

    def _get_updated_detections(self, detections: List[Detection]) -> List[Detection]:
        for det in detections:
            for t_id, track in self.tracked_objects.items():
                if track.box == det.box:
                    det.track_id = t_id
                    break
        return detections

    def get_summary(self) -> Dict[str, int]:
        return {
            "active_tracks": len(self.tracked_objects),
            "total_entered": self.total_entered,
            "total_exited": self.total_exited,
        }
