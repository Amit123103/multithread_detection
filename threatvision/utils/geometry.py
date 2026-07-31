"""Geometry and spatial math utilities."""

from typing import List, Tuple
import numpy as np


def compute_iou(
    boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]
) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes (xmin, ymin, xmax, ymax)."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return float(iou)


def box_centroid(box: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """Return the center point (cx, cy) of a bounding box."""
    return (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))


def point_in_polygon(point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
    """Ray-casting algorithm to test if point (x, y) is inside polygon."""
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
