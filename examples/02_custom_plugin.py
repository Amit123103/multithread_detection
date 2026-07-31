"""Example 02: Custom Plugin Development."""

from typing import List
import numpy as np
from threatvision import Detection, Plugin, ThreatVision, register_plugin

@register_plugin
class HardHatDetector(Plugin):
    """Custom plugin detecting safety hard hats."""

    def __init__(self, name: str = "hardhat"):
        super().__init__(name=name)

    def detect(self, frame: np.ndarray) -> List[Detection]:
        # Custom image processing or custom neural model invocation
        h, w = frame.shape[:2]
        return [
            Detection(
                label="hardhat",
                confidence=0.92,
                box=(int(w * 0.4), int(h * 0.1), int(w * 0.6), int(h * 0.3)),
                category="safety_gear",
            )
        ]

def main():
    print("Testing custom plugin detector...")
    tv = ThreatVision(camera=0)
    
    # Register custom plugin
    plugin_detector = HardHatDetector()
    tv.add_custom_detector(plugin_detector)
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    eval_result, detections = tv.process_single_frame(dummy_frame)
    
    print("Detections found:", [d.label for d in detections])
    print("Threat Score:", eval_result.score)

if __name__ == "__main__":
    main()
