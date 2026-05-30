"""
Pure-function tests for the Platt calibration sigmoid math.

Tests only the mathematical transform — no model loading, no data loading,
no API interaction.

Equation under test (OTD-019 Option A):
    calibrated_probability = sigmoid(coefficient * raw_score + intercept)
    where sigmoid(x) = 1 / (1 + exp(-x))
    raw_score is the raw model output probability in [0, 1].

Usage (from repo root):
    .\\venv\\Scripts\\python.exe -m pytest ml/lstm/scripts/test_platt_transform.py -v
"""

import math

import pytest


def platt_sigmoid(raw_score: float, coefficient: float, intercept: float) -> float:
    """Apply Platt calibration: sigmoid(coefficient * raw_score + intercept).

    Standalone copy of the transform for pure testing — must match the
    function in create_platt_calibration.py exactly.
    """
    x = coefficient * raw_score + intercept
    return 1.0 / (1.0 + math.exp(-x))


class TestPlattSigmoid:
    """Test the Platt sigmoid transform math."""

    def test_sigmoid_at_zero(self):
        """sigmoid(0) = 0.5 — when coeff*raw + intercept == 0."""
        # coefficient=1, raw_score=0, intercept=0 -> sigmoid(0) = 0.5
        result = platt_sigmoid(0.0, 1.0, 0.0)
        assert result == pytest.approx(0.5, abs=1e-10)

    def test_identity_coefficients(self):
        """With coefficient=0 and intercept=0, result should always be 0.5."""
        for raw in [0.0, 0.1, 0.5, 0.9, 1.0]:
            result = platt_sigmoid(raw, 0.0, 0.0)
            assert result == pytest.approx(0.5, abs=1e-10), (
                f"With coeff=0, intercept=0, raw={raw}: expected 0.5, got {result}"
            )

    def test_large_positive_input(self):
        """Large positive input should give result close to 1.0."""
        result = platt_sigmoid(0.9, 100.0, 0.0)
        assert result > 0.999

    def test_large_negative_input(self):
        """Large negative effective input should give result close to 0.0."""
        result = platt_sigmoid(0.1, 100.0, -50.0)
        # 100 * 0.1 + (-50) = -40 -> sigmoid(-40) ~ 0
        assert result < 0.001

    def test_output_always_in_unit_interval(self):
        """Output must always be in (0, 1) for any finite inputs."""
        test_cases = [
            (0.0, 1.0, 0.0),
            (0.5, 10.0, -5.0),
            (1.0, -10.0, 5.0),
            (0.0, 0.0, 0.0),
            (0.5, 1000.0, -500.0),
            (0.5, -1000.0, 500.0),
            (0.001, 1.0, 0.0),
            (0.999, 1.0, 0.0),
        ]
        for raw, coeff, intercept in test_cases:
            result = platt_sigmoid(raw, coeff, intercept)
            assert 0.0 < result < 1.0, (
                f"raw={raw}, coeff={coeff}, intercept={intercept}: "
                f"result {result} not in (0, 1)"
            )

    def test_monotonicity_positive_coefficient(self):
        """With positive coefficient, higher raw_score -> higher calibrated prob."""
        coeff = 5.0
        intercept = -2.0
        prev = 0.0
        for raw in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
            result = platt_sigmoid(raw, coeff, intercept)
            assert result > prev or raw == 0.0, (
                f"Not monotonic at raw={raw}: {result} <= {prev}"
            )
            prev = result

    def test_monotonicity_negative_coefficient(self):
        """With negative coefficient, higher raw_score -> lower calibrated prob."""
        coeff = -5.0
        intercept = 2.0
        prev = 1.0
        for raw in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
            result = platt_sigmoid(raw, coeff, intercept)
            assert result < prev or raw == 0.0, (
                f"Not monotonically decreasing at raw={raw}: {result} >= {prev}"
            )
            prev = result

    def test_known_value(self):
        """Test against a hand-computed value.

        coefficient=2.0, raw_score=0.3, intercept=-1.0
        x = 2.0 * 0.3 + (-1.0) = -0.4
        sigmoid(-0.4) = 1 / (1 + exp(0.4)) = 1 / (1 + 1.49182...) = 0.40131...
        """
        result = platt_sigmoid(0.3, 2.0, -1.0)
        expected = 1.0 / (1.0 + math.exp(0.4))
        assert result == pytest.approx(expected, abs=1e-10)

    def test_symmetry(self):
        """sigmoid(x) + sigmoid(-x) = 1 for the same effective input."""
        coeff = 3.0
        raw = 0.5
        # intercept = 1.0 -> x = 3*0.5 + 1 = 2.5
        r1 = platt_sigmoid(raw, coeff, 1.0)
        # intercept = -1.0 - 2*coeff*raw = -1 - 3 = -4 -> x = 3*0.5 + (-4) = -2.5
        r2 = platt_sigmoid(raw, coeff, -1.0 - 2 * coeff * raw)
        assert r1 + r2 == pytest.approx(1.0, abs=1e-10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
