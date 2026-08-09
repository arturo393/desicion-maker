"""
Unit tests for the NormalizationEngine module.
Usage: pytest python/tests/test_normalization.py
Does NOT: Run full decision pipeline integration tests.
"""

from __future__ import annotations

import numpy as np

from decision_maker.core.normalization import NormalizationEngine, NormalizationMethod


def test_min_max_normalization():
    vals = [10.0, 20.0, 30.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.MIN_MAX, maximize=True)
    assert np.isclose(normed[0], 0.0)
    assert np.isclose(normed[1], 0.5)
    assert np.isclose(normed[2], 1.0)


def test_min_max_minimize():
    vals = [10.0, 20.0, 30.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.MIN_MAX, maximize=False)
    assert np.isclose(normed[0], 1.0)
    assert np.isclose(normed[1], 0.5)
    assert np.isclose(normed[2], 0.0)


def test_vector_normalization():
    vals = [3.0, 4.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.VECTOR, maximize=True)
    assert np.isclose(normed[0], 0.6)
    assert np.isclose(normed[1], 0.8)


def test_vector_normalization_minimize():
    vals = [3.0, 4.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.VECTOR, maximize=False)
    assert np.isclose(normed[0], 0.4)
    assert np.isclose(normed[1], 0.2)


def test_z_score_normalization():
    vals = [10.0, 20.0, 30.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.Z_SCORE, maximize=True)
    assert np.isclose(normed.mean(), 0.0)
    assert normed[1] > normed[0]


def test_z_score_normalization_minimize():
    vals = [10.0, 20.0, 30.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.Z_SCORE, maximize=False)
    assert np.isclose(normed.mean(), 0.0)
    assert normed[0] > normed[2]


def test_max_relative_normalization():
    vals = [10.0, 20.0, 40.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.MAX_RELATIVE, maximize=True)
    assert np.isclose(normed[2], 1.0)
    assert np.isclose(normed[0], 0.25)


def test_max_relative_normalization_minimize():
    vals = [10.0, 20.0, 40.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.MAX_RELATIVE, maximize=False)
    assert np.isclose(normed[0], 0.75)
    assert np.isclose(normed[2], 0.0)


def test_empty_array_returns_empty():
    normed = NormalizationEngine.normalize_array([])
    assert len(normed) == 0


def test_constant_array_no_division_error():
    vals = [5.0, 5.0, 5.0]
    normed = NormalizationEngine.normalize_array(vals, method=NormalizationMethod.MIN_MAX)
    assert np.all(np.isfinite(normed))


def test_normalize_matrix():
    matrix = {
        "A": {"Cost": 100.0, "Quality": 80.0},
        "B": {"Cost": 200.0, "Quality": 90.0},
    }
    max_map = {"Cost": False, "Quality": True}
    normed = NormalizationEngine.normalize_matrix(matrix, max_map, method=NormalizationMethod.MIN_MAX)
    assert np.isclose(normed["A"]["Cost"], 1.0)  # Cheaper is better
    assert np.isclose(normed["B"]["Cost"], 0.0)
    assert np.isclose(normed["B"]["Quality"], 1.0)
