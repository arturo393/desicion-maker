from decision_maker.core.bootstrap import BootstrapConfig, BootstrapRanking


class TestBootstrapRanking:
    def test_confidence_intervals_basic(self):
        data = {
            "A": {"X": (1, 2, 3), "Y": (4, 5, 6)},
            "B": {"X": (2, 3, 4), "Y": (3, 4, 5)},
        }
        result = BootstrapRanking.confidence_intervals(
            data, BootstrapConfig(weights=[0.5, 0.5], maximize=[True, True], n_bootstrap=50)
        )
        assert "A" in result
        assert "B" in result
        assert "mean_rank" in result["A"]
        assert "ci_low" in result["A"]
        assert "ci_high" in result["A"]
        assert "p_best" in result["A"]
        assert 0 <= result["A"]["p_best"] <= 1

    def test_single_option(self):
        data = {"Only": {"X": (1, 2, 3)}}
        result = BootstrapRanking.confidence_intervals(data, BootstrapConfig(weights=[1.0], maximize=[True], n_bootstrap=10))
        assert result["Only"]["p_best"] == 1.0

    def test_empty_data(self):
        result = BootstrapRanking.confidence_intervals({}, BootstrapConfig(weights=[], maximize=[]))
        assert result == {}

    def test_perturbed_fuzzy_numbers_are_sorted(self, monkeypatch):
        """Noise added to triangular fuzzy numbers must preserve a <= b <= c order."""
        import numpy as np

        from decision_maker.core.topsis import TOPSISEngine

        captured_data = []
        original_analyze = TOPSISEngine.analyze

        def mock_analyze(self_eng, matrix, weights, maximize):
            captured_data.append(matrix)
            return original_analyze(self_eng, matrix, weights, maximize)

        class MockRNG:
            def normal(self, loc, scale, size):
                return np.array([10.0, 0.0, -10.0])

        monkeypatch.setattr(TOPSISEngine, "analyze", mock_analyze)
        monkeypatch.setattr(np.random, "default_rng", lambda seed=None: MockRNG())

        data = {
            "A": {"X": (1.0, 2.0, 3.0)},
            "B": {"X": (2.0, 3.0, 4.0)},
        }
        BootstrapRanking.confidence_intervals(
            data, BootstrapConfig(weights=[1.0], maximize=[True], n_bootstrap=2)
        )

        assert len(captured_data) > 0
        for boot_matrix in captured_data:
            for opt_vals in boot_matrix.values():
                for f_vals in opt_vals.values():
                    a, b, c = f_vals
                    assert a <= b <= c, f"Fuzzy number not sorted: ({a}, {b}, {c})"

    def test_confidence_intervals_reproducibility_with_seed(self):
        """Identical seed produces identical bootstrap confidence intervals; different seeds produce different ones."""
        data = {
            "OptionA": {"F1": (1.0, 2.0, 3.0), "F2": (2.0, 3.0, 4.0)},
            "OptionB": {"F1": (1.5, 2.0, 2.5), "F2": (1.0, 3.0, 5.0)},
        }
        cfg_seed_42_a = BootstrapConfig(weights=[0.5, 0.5], maximize=[True, True], n_bootstrap=50, seed=42)
        cfg_seed_42_b = BootstrapConfig(weights=[0.5, 0.5], maximize=[True, True], n_bootstrap=50, seed=42)
        cfg_seed_99 = BootstrapConfig(weights=[0.5, 0.5], maximize=[True, True], n_bootstrap=50, seed=99)

        res1 = BootstrapRanking.confidence_intervals(data, cfg_seed_42_a)
        res2 = BootstrapRanking.confidence_intervals(data, cfg_seed_42_b)
        res3 = BootstrapRanking.confidence_intervals(data, cfg_seed_99)

        # Same seed => identical intervals
        assert res1 == res2
        # Different seed => distinct intervals
        assert res1 != res3

        # Parameter override takes precedence over config.seed
        res_param_42 = BootstrapRanking.confidence_intervals(data, cfg_seed_99, seed=42)
        assert res_param_42 == res1
