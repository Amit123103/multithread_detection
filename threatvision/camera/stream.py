"""Camera Stream Reader supporting Laptop camera, USB webcam, RTSP, Video files, Images, and Multi-Camera setups."""

import threading
import time
from typing import Generator, List, Tuple, Union
import cv2
import numpy as np


class CameraStream:
    """Threaded Camera & Video Stream Reader."""

    def __init__(
        self,
        source: Union[int, str] = 0,
        skip_frames: int = 0,
        width: int = 1280,
        height: int = 720,
    ):
        self.source = source
        self.skip_frames = skip_frames
        self.width = width
        self.height = height

        self.cap: cv2.VideoCapture | None = None
        self.is_image = False
        self.image_frame: np.ndarray | None = None

        self.stopped = False
        self.frame: np.ndarray | None = None
        self.lock = threading.Lock()
        self.frame_count = 0

        self._init_source()

    def _init_source(self) -> None:
        if isinstance(self.source, str) and (
            self.source.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))
        ):
            self.is_image = True
            self.image_frame = cv2.imread(self.source)
            if self.image_frame is None:
                # Generate synthetic fallback frame if path doesn't exist
                self.image_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(
                    self.image_frame,
                    "THREATVISION TEST STREAM",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )
            self.frame = self.image_frame
            return

        self.cap = cv2.VideoCapture(self.source)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def start(self) -> "CameraStream":
        """Start threaded frame capture loop."""
        if self.is_image or self.cap is None:
            return self

        t = threading.Thread(target=self._update, daemon=True)
        t.start()
        return self

    def _update(self) -> None:
        while not self.stopped and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # If video file loop back to start
                if isinstance(self.source, str) and not self.source.startswith("rtsp"):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.01)
                    continue

            self.frame_count += 1
            if self.skip_frames > 0 and (self.frame_count % (self.skip_frames + 1) != 0):
                continue

            with self.lock:
                self.frame = frame

    def read(self) -> Tuple[bool, np.ndarray | None]:
        """Read latest frame."""
        if self.is_image:
            return True, self.image_frame.copy() if self.image_frame is not None else None

        with self.lock:
            if self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def release(self) -> None:
        """Stop reader and release hardware/file descriptors."""
        self.stopped = True
        if self.cap and self.cap.isOpened():
            self.cap.release()


class MultiCameraManager:
    """Manages multiple simultaneous live camera feeds."""

    def __init__(self, sources: List[Union[int, str]]):
        self.streams = [CameraStream(src).start() for src in sources]

    def read_all(self) -> List[Tuple[bool, np.ndarray | None]]:
        return [stream.read() for stream in self.streams]

    def release_all(self) -> None:
        for stream in self.streams:
            stream.release()
