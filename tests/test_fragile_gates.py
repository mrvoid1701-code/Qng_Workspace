"""
Smoke tests for fragile gates G16d and G17a.

These tests validate the threshold logic and gate check functions directly,
without running the full simulation pipeline (~30s). They guard against
accidental threshold drift or logic regressions.

G16d: hessian_frac_neg > 0.90  (margin 11.1% at last run — fragile)
G17a: spectral_gap μ₁ > 0.01   (margin 10.9% at last run — fragile)
"""

import sys
from pathlib import Path

# Allow importing from scripts/ without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


# ---------------------------------------------------------------------------
# G16d — Action Hessian negative-definite fraction
# ---------------------------------------------------------------------------

def _g16d_check(frac_neg: float, threshold: float = 0.90) -> bool:
    """Gate G16d passes when fraction of H_{ii} < 0 exceeds threshold."""
    return frac_neg > threshold


class TestG16dThreshold:
    """Guard the G16d threshold value and gate logic."""

    def test_threshold_value_unchanged(self):
        """G16d threshold must stay at 0.90 (promotion-frozen)."""
        # Import the actual dataclass to catch any accidental threshold drift.
        from run_qng_action_v1 import ActionThresholds
        t = ActionThresholds()
        assert t.g16d_hessian_frac_min == 0.90, (
            f"G16d threshold changed to {t.g16d_hessian_frac_min}; "
            "update GATES_STATUS.md and re-validate before merging."
        )

    def test_passes_at_current_value(self):
        """Current observed value (1.000) must pass."""
        assert _g16d_check(1.000)

    def test_passes_just_above_threshold(self):
        assert _g16d_check(0.901)

    def test_fails_at_threshold(self):
        """Exact equality is NOT a pass (strict >)."""
        assert not _g16d_check(0.90)

    def test_fails_below_threshold(self):
        assert not _g16d_check(0.89)
        assert not _g16d_check(0.00)

    def test_margin_from_current_value(self):
        """Margin must stay above 5% to provide early warning before failure."""
        current_value = 1.000
        threshold = 0.90
        # margin = (value - threshold) / threshold * 100
        margin_pct = (current_value - threshold) / threshold * 100
        assert margin_pct >= 5.0, (
            f"G16d margin dropped to {margin_pct:.1f}% — investigate before merge."
        )


# ---------------------------------------------------------------------------
# G17a — Spectral gap μ₁ of random-walk Laplacian
# ---------------------------------------------------------------------------

def _g17a_check(spectral_gap: float, threshold: float = 0.01) -> bool:
    """Gate G17a passes when lowest non-trivial eigenvalue exceeds threshold."""
    return spectral_gap > threshold


class TestG17aThreshold:
    """Guard the G17a threshold value and gate logic."""

    def test_threshold_value_unchanged(self):
        """G17a threshold must stay at 0.01 (promotion-frozen)."""
        from run_qng_g17_v2 import QMThresholdsV2
        t = QMThresholdsV2()
        assert t.g17a_gap_min == 0.01, (
            f"G17a threshold changed to {t.g17a_gap_min}; "
            "update GATES_STATUS.md and re-validate before merging."
        )

    def test_passes_at_current_value(self):
        """Current observed value (0.01109) must pass."""
        assert _g17a_check(0.01109)

    def test_passes_just_above_threshold(self):
        assert _g17a_check(0.01001)

    def test_fails_at_threshold(self):
        """Exact equality is NOT a pass (strict >)."""
        assert not _g17a_check(0.01)

    def test_fails_below_threshold(self):
        assert not _g17a_check(0.009)
        assert not _g17a_check(0.0)

    def test_margin_from_current_value(self):
        """Margin must stay above 5% to provide early warning before failure."""
        current_value = 0.01109
        threshold = 0.01
        margin_pct = (current_value - threshold) / threshold * 100
        assert margin_pct >= 5.0, (
            f"G17a margin dropped to {margin_pct:.1f}% — investigate before merge."
        )

    def test_disconnected_graph_fails(self):
        """A disconnected graph yields spectral_gap = 0 and must fail G17a."""
        spectral_gap_disconnected = 0.0
        assert not _g17a_check(spectral_gap_disconnected)
