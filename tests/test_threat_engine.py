"""Unit tests for ThreatEngine."""

from threatvision.analytics.threat_engine import ThreatEngine, ThreatLevel
from threatvision.models.backend import Detection


def test_threat_engine_safe():
    engine = ThreatEngine()
    eval_result = engine.evaluate([])
    assert eval_result.level == ThreatLevel.SAFE
    assert eval_result.score == 0.0


def test_threat_engine_weapon_hazard():
    engine = ThreatEngine()
    gun_det = Detection(
        label="gun", confidence=0.95, box=(10, 10, 50, 50), category="weapon"
    )
    eval_result = engine.evaluate([gun_det])

    assert eval_result.score > 0.85
    assert eval_result.level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL)
    assert "gun" in eval_result.primary_threat


def test_threat_engine_compounding():
    engine = ThreatEngine()
    det1 = Detection(
        label="gun", confidence=0.9, box=(10, 10, 50, 50), category="weapon"
    )
    det2 = Detection(
        label="fire", confidence=0.9, box=(60, 60, 100, 100), category="fire"
    )

    eval_single = engine.evaluate([det1])
    eval_multi = engine.evaluate([det1, det2])

    assert eval_multi.score >= eval_single.score
