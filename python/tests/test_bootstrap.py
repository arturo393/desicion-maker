from python.core.bootstrap import BootstrapRanking


class TestBootstrapRanking:
    def test_confidence_intervals_basic(self):
        data = {
            "A": {"X": (1, 2, 3), "Y": (4, 5, 6)},
            "B": {"X": (2, 3, 4), "Y": (3, 4, 5)},
        }
        result = BootstrapRanking.confidence_intervals(data, [0.5, 0.5], [True, True], n_bootstrap=50)
        assert "A" in result
        assert "B" in result
        assert "mean_rank" in result["A"]
        assert "ci_low" in result["A"]
        assert "ci_high" in result["A"]
        assert "p_best" in result["A"]
        assert 0 <= result["A"]["p_best"] <= 1

    def test_single_option(self):
        data = {"Only": {"X": (1, 2, 3)}}
        result = BootstrapRanking.confidence_intervals(data, [1.0], [True], n_bootstrap=10)
        assert result["Only"]["p_best"] == 1.0

    def test_empty_data(self):
        result = BootstrapRanking.confidence_intervals({}, [], [])
        assert result == {}
