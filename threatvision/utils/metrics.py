"""Performance and system metrics monitor."""

import time
from typing import Any, Dict

import psutil


class PerformanceMonitor:
    """Calculates FPS, latency per frame, and memory consumption."""

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times: list[float] = []
        self.last_timestamp = time.time()
        self.inference_latencies: list[float] = []

    def tick(self) -> None:
        """Call at start of frame process."""
        self.last_timestamp = time.time()

    def tock(self, inference_time_sec: float = 0.0) -> float:
        """Call at end of frame process. Returns current FPS."""
        now = time.time()
        elapsed = now - self.last_timestamp
        if elapsed > 0:
            self.frame_times.append(1.0 / elapsed)
            if len(self.frame_times) > self.window_size:
                self.frame_times.pop(0)

        if inference_time_sec > 0:
            self.inference_latencies.append(inference_time_sec)
            if len(self.inference_latencies) > self.window_size:
                self.inference_latencies.pop(0)

        return self.get_fps()

    def get_fps(self) -> float:
        """Return average FPS over window size."""
        if not self.frame_times:
            return 0.0
        return sum(self.frame_times) / len(self.frame_times)

    def get_avg_latency_ms(self) -> float:
        """Return average model inference latency in milliseconds."""
        if not self.inference_latencies:
            return 0.0
        return (sum(self.inference_latencies) / len(self.inference_latencies)) * 1000.0

    @staticmethod
    def get_system_resources() -> Dict[str, Any]:
        """Fetch current CPU, RAM, and system resource statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": round(psutil.virtual_memory().used / (1024 * 1024), 2),
        }
