"""Regression tests for integrity checking and pathology count arithmetic."""
import copy
import math

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from ihc_multiplex_quant_agent.pdl1_scorer import compute_pdl1_cps, PDL1Scorer
from ihc_multiplex_quant_agent.spatial_analysis import SpatialAnalyzer, compute_spatial_distances


def test_audit_detects_tampering_and_cannot_be_mutated_from_getter():
    audit = AuditTrail(secret_key="unit-test-fixed-key")
    audit.log("worker", "system", "test", {"case": "sample-01"})
    audit.log("worker", "system", "test", {"case": "sample-02"})
    assert audit.verify_integrity()
    external = audit.get_trail()
    external[0]["actor"] = "attacker"
    assert audit.verify_integrity()
    audit.logs[0]["actor"] = "attacker"
    assert not audit.verify_integrity()


def test_audit_detects_recomputed_link_after_bad_signature():
    audit = AuditTrail(secret_key="unit-test-fixed-key")
    audit.log("worker", "system", "test", {"case": "sample-01"})
    audit.log("worker", "system", "test", {"case": "sample-02"})
    audit.logs[0]["payload_hash"] = "0" * 64
    assert not audit.verify_integrity()


def test_nested_phi_is_rejected():
    payload = SystemTaskPayload(
        task_id="T-01", target_identifier="SYNTH-01", primary_metric=5.0,
        attributes={"metadata": {"notes": "patient@example.com"}},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_metric_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T-01", target_identifier="SYNTH-01", primary_metric=value)


def test_even_spatial_median():
    result = compute_spatial_distances(
        [{"x": 0, "y": 0}],
        [{"x": 2, "y": 0}, {"x": 6, "y": 0}],
        "CD8",
    )
    assert result["median_dist_um"] == 4.0


def test_hotspot_density_units():
    result = SpatialAnalyzer().compute_hotspot_density(
        [{"x": 1, "y": 1}] * 5, grid_size=100, threshold=5
    )["hotspots"][0]
    assert result["density_per_100um2"] == 0.05
    assert result["density_per_mm2"] == 500.0


def test_hotspot_invalid_grid():
    with pytest.raises(ValueError):
        SpatialAnalyzer().compute_hotspot_density([{"x": 1, "y": 1}], grid_size=0)


def test_cps_numerator_and_cap():
    result = compute_pdl1_cps(100, 40, 80)
    assert result["cps"] == 100.0
    assert result["valid"]
    assert result["pembrolizumab_eligible"] is None


def test_cps_invalid_counts():
    assert not compute_pdl1_cps(100, 101, 0)["valid"]
    assert not compute_pdl1_cps(100, 50, -1)["valid"]
    assert not PDL1Scorer().compute_tps(100, 101)["valid"]
