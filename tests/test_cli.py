"""Unit tests for ThreatVision CLI."""

from click.testing import CliRunner
import pytest
from threatvision.cli.cli import main

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output

def test_cli_benchmark():
    runner = CliRunner()
    result = runner.invoke(main, ["benchmark", "-n", "5"])
    assert result.exit_code == 0
    assert "FPS" in result.output

def test_cli_config(tmp_path):
    output_cfg = tmp_path / "test_config.yaml"
    runner = CliRunner()
    result = runner.invoke(main, ["config", "-o", str(output_cfg)])
    assert result.exit_code == 0
    assert output_cfg.exists()
