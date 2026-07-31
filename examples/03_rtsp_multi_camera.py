"""Example 03: RTSP & Multi-Camera Processing."""

from threatvision.camera import MultiCameraManager
from threatvision.engine import ThreatVision

def main():
    print("Initializing Multi-Camera RTSP Stream Manager...")
    
    camera_sources = [
        0,  # Local USB Webcam
        "rtsp://192.168.1.100:554/stream1",  # RTSP Camera 1
        "sample_feed.mp4"  # Video File
    ]

    manager = MultiCameraManager(camera_sources)
    print(f"Active camera streams: {len(manager.streams)}")

    tv = ThreatVision(camera=0)
    tv.enable_person_detection()
    tv.enable_weapon_detection()

    frames = manager.read_all()
    print(f"Captured frames count: {len(frames)}")

    manager.release_all()

if __name__ == "__main__":
    main()
