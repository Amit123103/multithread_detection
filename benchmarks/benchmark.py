"""Benchmark testing script for ThreatVision AI frame processing throughput."""

import time
import numpy as np
from threatvision.engine import ThreatVision

def run_benchmark(num_frames: int = 200):
    print(f"Starting ThreatVision AI Performance Benchmark on {num_frames} frames...")
    
    tv = ThreatVision(image="synthetic.jpg")
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()
    tv.enable_fight_detection()

    dummy_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

    latencies = []
    start_total = time.time()

    for _ in range(num_frames):
        t0 = time.time()
        tv.process_single_frame(dummy_frame)
        latencies.append((time.time() - t0) * 1000.0)

    total_time = time.time() - start_total
    avg_fps = num_frames / total_time
    avg_latency = sum(latencies) / len(latencies)

    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Frames Processed : {num_frames}")
    print(f"Total Processing Time  : {total_time:.2f} seconds")
    print(f"Average Throughput     : {avg_fps:.2f} FPS")
    print(f"Average Latency/Frame  : {avg_latency:.2f} ms")
    print("====================================================\n")

if __name__ == "__main__":
    run_benchmark(200)
