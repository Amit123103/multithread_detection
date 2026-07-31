"""Command Line Interface (CLI) for ThreatVision AI."""

import sys
import time

import click
from rich.console import Console
from rich.table import Table

from threatvision import ThreatVision, __version__
from threatvision.config.config import ThreatVisionConfig

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="threatvision-ai")
def main():
    """ThreatVision AI — Security Command Center & Threat Detection CLI."""
    pass


@main.command()
@click.option("--source", "-s", default=0, help="Camera index or RTSP stream URL.")
@click.option("--dashboard/--no-dashboard", default=True, help="Enable live web dashboard.")
@click.option("--port", "-p", default=8000, help="Dashboard port.")
def camera(source: str | int, dashboard: bool, port: int):
    """Run real-time threat detection on camera feed."""
    try:
        src = int(source) if str(source).isdigit() else source
    except ValueError:
        src = source

    console.print(f"[bold green]Starting ThreatVision AI on camera source:[/] {src}")

    cfg = ThreatVisionConfig()
    cfg.dashboard_port = port

    tv = ThreatVision(camera=src, dashboard=dashboard, config=cfg)
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()
    tv.enable_fight_detection()

    tv.start(block=True)


@main.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option("--dashboard/--no-dashboard", default=True, help="Enable live web dashboard.")
def video(video_path: str, dashboard: bool):
    """Process a recorded video file."""
    console.print(f"[bold blue]Processing video file:[/] {video_path}")
    tv = ThreatVision(video=video_path, dashboard=dashboard)
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()
    tv.start(block=True)


@main.command()
@click.argument("image_path", type=click.Path(exists=True))
def image(image_path: str):
    """Process a single image file and print detection results."""
    import cv2
    console.print(f"[bold cyan]Analyzing image file:[/] {image_path}")

    frame = cv2.imread(image_path)
    if frame is None:
        console.print("[bold red]Failed to load image file.[/]")
        sys.exit(1)

    tv = ThreatVision(image=image_path)
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()

    eval_result, detections = tv.process_single_frame(frame)

    table = Table(title=f"ThreatVision Analysis — {image_path}")
    table.add_column("Label", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Confidence", style="green")
    table.add_column("Bounding Box", style="yellow")

    for d in detections:
        table.add_row(d.label, d.category, f"{int(d.confidence*100)}%", str(d.box))

    console.print(table)
    console.print(f"\n[bold]Threat Level:[/] [bold red]{eval_result.level.value}[/]")
    console.print(f"[bold]Threat Score:[/] {int(eval_result.score * 100)}%")
    console.print(f"[bold]Recommendation:[/] {eval_result.recommendation}")


@main.command()
@click.option("--host", default="127.0.0.1", help="Host address.")
@click.option("--port", "-p", default=8000, help="Dashboard port.")
def dashboard(host: str, port: int):
    """Launch standalone ThreatVision Web Dashboard & REST API server."""
    import uvicorn

    from threatvision.api.app import app

    console.print(f"[bold green]Launching ThreatVision Dashboard on http://{host}:{port}[/]")
    uvicorn.run(app, host=host, port=port)


@main.command()
@click.option("--frames", "-n", default=100, help="Number of test frames.")
def benchmark(frames: int):
    """Run performance and FPS latency benchmark."""
    import numpy as np

    console.print(f"[bold yellow]Running ThreatVision Benchmark on {frames} frames...[/]")

    tv = ThreatVision(image="synthetic.jpg")
    tv.enable_person_detection()
    tv.enable_weapon_detection()
    tv.enable_fire_detection()

    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    start = time.time()
    for _ in range(frames):
        tv.process_single_frame(dummy_frame)
    elapsed = time.time() - start

    fps = frames / elapsed
    ms_per_frame = (elapsed / frames) * 1000.0

    table = Table(title="ThreatVision AI Performance Benchmark")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total Frames", str(frames))
    table.add_row("Total Elapsed", f"{elapsed:.2f} s")
    table.add_row("Average Throughput", f"{fps:.2f} FPS")
    table.add_row("Avg Latency / Frame", f"{ms_per_frame:.2f} ms")

    console.print(table)


@main.command()
@click.option("--output", "-o", default="config.yaml", help="Output file path.")
def config(output: str):
    """Generate default ThreatVision YAML configuration file."""
    cfg = ThreatVisionConfig()
    cfg.save_to_file(output)
    console.print(f"[bold green]Saved default configuration file to:[/] {output}")


if __name__ == "__main__":
    main()
