"""Example 01: Basic Threat Detection."""

import time
from threatvision import ThreatVision

def main():
    print("Starting ThreatVision AI Basic Example...")

    tv = ThreatVision(
        camera=0,
        dashboard=True,
        save_incidents=True,
    )

    tv.enable_person_detection(threshold=0.5)
    tv.enable_weapon_detection(threshold=0.6)
    tv.enable_fire_detection(threshold=0.55)
    tv.enable_fight_detection(threshold=0.6)
    tv.enable_smoke_detection(threshold=0.55)

    tv.start()

    print("ThreatVision running. Access dashboard at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            stats = tv.get_statistics()
            print(f"Stats: FPS={stats['fps']}, Threat Score={int(stats['threat_score']*100)}%, Level={stats['threat_level']}")
            time.sleep(2)
    except KeyboardInterrupt:
        tv.stop()
        print("ThreatVision stopped.")

if __name__ == "__main__":
    main()
