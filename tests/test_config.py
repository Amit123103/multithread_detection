"""Unit tests for ThreatVisionConfig."""

from pathlib import Path

from threatvision.config.config import ThreatVisionConfig


def test_default_config():
    config = ThreatVisionConfig()
    assert config.camera.fps == 30
    assert config.dashboard_port == 8000
    assert "person" in config.detectors
    assert "weapon" in config.detectors


def test_save_and_load_yaml(tmp_path: Path):
    yaml_file = tmp_path / "config.yaml"
    config = ThreatVisionConfig()
    config.camera.fps = 60
    config.save_to_file(yaml_file)

    assert yaml_file.exists()
    loaded = ThreatVisionConfig.load_from_file(yaml_file)
    assert loaded.camera.fps == 60


def test_save_and_load_json(tmp_path: Path):
    json_file = tmp_path / "config.json"
    config = ThreatVisionConfig()
    config.dashboard_port = 9000
    config.save_to_file(json_file)

    assert json_file.exists()
    loaded = ThreatVisionConfig.load_from_file(json_file)
    assert loaded.dashboard_port == 9000
