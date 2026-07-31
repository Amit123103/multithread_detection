"""Visual rendering utilities for HUD, bounding boxes, labels, and status badges."""

from typing import Tuple

import cv2
import numpy as np

THREAT_COLORS = {
    "SAFE": (0, 255, 127),       # Spring Green
    "LOW": (0, 215, 255),        # Gold/Yellow
    "MEDIUM": (0, 140, 255),     # Orange
    "HIGH": (0, 69, 255),        # Red-Orange
    "CRITICAL": (0, 0, 255),     # Bright Red
}


def draw_bounding_box(
    frame: np.ndarray,
    box: Tuple[int, int, int, int],
    label: str,
    confidence: float,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    track_id: int | None = None,
) -> np.ndarray:
    """Annotate bounding box and polished badge with confidence level on image frame."""
    xmin, ymin, xmax, ymax = [int(v) for v in box]

    # Draw rounded-corner bounding box
    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, thickness)

    # Label text
    id_str = f"#{track_id} " if track_id is not None else ""
    text = f"{id_str}{label.upper()} {int(confidence * 100)}%"

    # Draw label badge background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, font_thickness
    )

    badge_ymin = max(0, ymin - text_height - 10)
    badge_ymax = ymin if ymin - text_height - 10 >= 0 else ymin + text_height + 10

    cv2.rectangle(
        frame,
        (xmin, badge_ymin),
        (xmin + text_width + 10, badge_ymax),
        color,
        -1,
    )

    cv2.putText(
        frame,
        text,
        (xmin + 5, badge_ymax - 4),
        font,
        font_scale,
        (255, 255, 255),
        font_thickness,
        cv2.LINE_AA,
    )

    return frame


def draw_hud(
    frame: np.ndarray,
    fps: float,
    threat_score: float,
    threat_level: str,
    active_alerts_count: int,
) -> np.ndarray:
    """Render heads-up display (HUD) overlay bar at top of video frame."""
    h, w = frame.shape[:2]

    # Create semi-transparent top header bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), (15, 23, 42), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Draw logo/title
    cv2.putText(
        frame,
        "THREATVISION AI",
        (15, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Draw FPS
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (w - 140, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )

    # Draw Threat Level Badge
    color = THREAT_COLORS.get(threat_level, (0, 255, 0))
    badge_text = f"LEVEL: {threat_level} ({int(threat_score * 100)}%)"

    cv2.rectangle(frame, (250, 10), (520, 40), color, -1)
    cv2.putText(
        frame,
        badge_text,
        (260, 31),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0) if threat_level in ("SAFE", "LOW") else (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return frame
