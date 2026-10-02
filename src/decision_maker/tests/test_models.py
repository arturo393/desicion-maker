import numpy as np

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable


class TestUncertainVariable:
    def test_deterministic(self):
        var = UncertainVariable("Const", DistributionType.DETERMINISTIC, [10])
        samples = var.sample(100)
        assert np.all(samples == 10)

    def test_normal_stats(self):
        var = UncertainVariable("Norm", DistributionType.NORMAL, [100, 15])
        samples = var.sample(10000)
        assert abs(np.mean(samples) - 100) < 1.0
        assert abs(np.std(samples) - 15) < 1.0

    def test_uniform_range(self):
        var = UncertainVariable("Uni", DistributionType.UNIFORM, [0, 10])
        samples = var.sample(1000)
        assert np.all((samples >= 0) & (samples <= 10))

    def test_triangular_unordered_params(self):
        var = UncertainVariable("Tri", DistributionType.TRIANGULAR, [10, 5, 20])
        samples = var.sample(100)
        assert np.all((samples >= 5) & (samples <= 20))

    def test_beta_range(self):
        var = UncertainVariable("Beta", DistributionType.BETA, [2, 5])
        samples = var.sample(1000)
        assert np.all((samples >= 0) & (samples <= 1))

    def test_lognormal_positive(self):
        var = UncertainVariable("LogN", DistributionType.LOGNORMAL, [0, 0.5])
        samples = var.sample(1000)
        assert np.all(samples > 0)

    def test_gamma_mean(self):
        var = UncertainVariable("Gamma", DistributionType.GAMMA, [2.0, 3.0])
        samples = var.sample(10000)
        assert abs(np.mean(samples) - 6.0) < 1.0

    def test_poisson(self):
        var = UncertainVariable("Pois", DistributionType.POISSON, [5])
        samples = var.sample(10000)
        assert np.all(samples >= 0)
        assert abs(np.mean(samples) - 5) < 0.5

    def test_bernoulli(self):
        var = UncertainVariable("Bern", DistributionType.BERNOULLI, [0.5])
        samples = var.sample(10000)
        assert np.all((samples == 0) | (samples == 1))
        assert abs(np.mean(samples) - 0.5) < 0.05

    def test_exponential(self):
        var = UncertainVariable("Exp", DistributionType.EXPONENTIAL, [2.0])
        samples = var.sample(10000)
        assert np.all(samples >= 0)
        assert abs(np.mean(samples) - 2.0) < 0.3

    def test_unknown_distribution_returns_zeros(self):
        class FakeDist:
            value = "fake"

        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UncertainVariable("Fake", FakeDist(), [1, 2, 3])

    def test_sample_size_zero(self):
        var = UncertainVariable("Empty", DistributionType.DETERMINISTIC, [5])
        samples = var.sample(0)
        assert len(samples) == 0

    def test_large_sample(self):
        var = UncertainVariable("Large", DistributionType.NORMAL, [0, 1])
        samples = var.sample(100000)
        assert len(samples) == 100000

    def test_validate_normal_negative_std(self):
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UncertainVariable("Bad", DistributionType.NORMAL, [0, -1])

    def test_validate_too_few_params(self):
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UncertainVariable("Bad", DistributionType.NORMAL, [0])

    def test_validate_ok(self):
        UncertainVariable("Ok", DistributionType.NORMAL, [0, 1])

    def test_nan_params_sanitized(self):
        # Inverted: Previously replaced NaN parameters with defaults silently; now raises ValueError.
        var = UncertainVariable("NaN", DistributionType.NORMAL, [float("nan"), float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_inf_params_sanitized(self):
        # Inverted: Previously replaced Inf parameters with defaults silently; now raises ValueError.
        var = UncertainVariable("Inf", DistributionType.NORMAL, [float("inf"), float("inf")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_negative_inf_params_sanitized(self):
        # Inverted: Previously replaced -Inf parameters with defaults silently; now raises ValueError.
        var = UncertainVariable("NegInf", DistributionType.NORMAL, [-float("inf"), float("inf")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_empty_params_defaults_used(self):
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UncertainVariable("Empty", DistributionType.NORMAL, [])

    def test_nan_deterministic(self):
        # Inverted: Previously returned 0 for NaN deterministic; now raises ValueError.
        var = UncertainVariable("NaN", DistributionType.DETERMINISTIC, [float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_nan_beta_sanitized(self):
        # Inverted: Previously sanitized NaN beta params to defaults; now raises ValueError.
        var = UncertainVariable("NaN", DistributionType.BETA, [float("nan"), float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_nan_uniform_sanitized(self):
        # Inverted: Previously sanitized NaN uniform params to defaults; now raises ValueError.
        var = UncertainVariable("NaN", DistributionType.UNIFORM, [float("nan"), float("inf")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_bernoulli_nan_clipped(self):
        # Inverted: Previously sanitized NaN bernoulli param to default; now raises ValueError.
        var = UncertainVariable("BNan", DistributionType.BERNOULLI, [float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_gamma_nan_sanitized(self):
        # Inverted: Previously sanitized NaN gamma params to defaults; now raises ValueError.
        var = UncertainVariable("GNan", DistributionType.GAMMA, [float("nan"), float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_lognormal_nan_sanitized(self):
        # Inverted: Previously sanitized NaN lognormal params to defaults; now raises ValueError.
        var = UncertainVariable("LNan", DistributionType.LOGNORMAL, [float("nan"), float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_poisson_nan_sanitized(self):
        # Inverted: Previously sanitized NaN poisson param to default; now raises ValueError.
        var = UncertainVariable("PNan", DistributionType.POISSON, [float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_exponential_nan_sanitized(self):
        # Inverted: Previously sanitized NaN exponential param to default; now raises ValueError.
        var = UncertainVariable("ENan", DistributionType.EXPONENTIAL, [float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_triangular_nan_sanitized(self):
        # Inverted: Previously sanitized NaN triangular params to defaults; now raises ValueError.
        var = UncertainVariable("TNan", DistributionType.TRIANGULAR, [float("nan"), float("nan"), float("nan")])
        import pytest
        with pytest.raises(ValueError, match="NaN or Inf"):
            var.sample(100)

    def test_sampling_failure_raises_value_error(self, monkeypatch):
        """When sampling fails, it must raise ValueError rather than returning zeros."""
        var = UncertainVariable("FailVar", DistributionType.NORMAL, [10.0, 1.0])
        import pytest

        from decision_maker.core import models

        def broken_sampler(params, size, rng=None):
            raise ValueError("Underlying sampler breakdown")

        monkeypatch.setitem(models.SAMPLE_DISPATCH, DistributionType.NORMAL, broken_sampler)
        with pytest.raises(ValueError, match="Sampling failed for variable 'FailVar'"):
            var.sample(100)


    def test_bernoulli_p_above_one_clipped(self):
        var = UncertainVariable("BHigh", DistributionType.BERNOULLI, [2.0])
        samples = var.sample(10000)
        assert np.all((samples == 0) | (samples == 1))
        assert abs(np.mean(samples) - 1.0) < 0.01

    def test_bernoulli_p_below_zero_clipped(self):
        var = UncertainVariable("BLow", DistributionType.BERNOULLI, [-1.0])
        samples = var.sample(10000)
        assert np.all((samples == 0) | (samples == 1))
        assert abs(np.mean(samples) - 0.0) < 0.01

    def test_exponential_zero_scale_uses_minimum(self):
        var = UncertainVariable("ExpZero", DistributionType.EXPONENTIAL, [0])
        samples = var.sample(1000)
        assert np.all(np.isfinite(samples))
        assert np.all(samples >= 0)

    def test_normal_zero_std_uses_minimum(self):
        var = UncertainVariable("NormZero", DistributionType.NORMAL, [5, 0])
        samples = var.sample(100)
        assert np.all(np.isfinite(samples))
        assert abs(np.mean(samples) - 5) < 0.1


class TestFactor:
    def test_factor_defaults(self):
        f = Factor("Test", 0.5)
        assert f.name == "Test"
        assert f.weight == 0.5
        assert f.maximize is True
        assert f.category == "General"

    def test_factor_minimize(self):
        f = Factor("Cost", 0.3, maximize=False, category="Financial")
        assert f.maximize is False
        assert f.category == "Financial"


class TestDecisionOption:
    def test_add_variable(self):
        opt = DecisionOption("Test", "Description")
        opt.add_variable("Speed", DistributionType.NORMAL, 100, 10)
        assert "Speed" in opt.variables
        assert opt.variables["Speed"].dist_type == DistributionType.NORMAL
        assert opt.variables["Speed"].params == [100, 10]

    def test_default_description(self):
        opt = DecisionOption("Test")
        assert opt.description == ""
        assert opt.variables == {}
