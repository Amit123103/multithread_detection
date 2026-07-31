"""Spatial analytics module for perimeter zones and loitering analysis."""

from typing import Dict, List, Tuple
from threatvision.tracking.tracker import TrackedObject
from threatvision.utils.geometry import point_in_polygon


class SpatialAnalytics:
    """Manages spatial perimeter zones and loitering detection."""

    def __init__(self, loitering_threshold_seconds: float = 10.0):
        self.zones: List[Dict] = []
        self.loitering_threshold_seconds = loitering_threshold_seconds

    def add_zone(self, name: str, polygon: List[Tuple[int, int]]) -> None:
        self.zones.append({"name": name, "polygon": polygon})

    def check_loitering(self, tracks: Dict[int, TrackedObject]) -> List[TrackedObject]:
        """Return list of tracked objects that have exceeded loitering duration."""
        loiterers = []
        for track in tracks.values():
            if track.dwell_time_seconds >= self.loitering_threshold_seconds:
                loiterers.append(track)
        return loiterers
