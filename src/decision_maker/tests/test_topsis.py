import math

from decision_maker.core.topsis import TOPSISEngine


class TestTOPSISEngine:
    def test_ranking(self):
        data = {
            "OptA": {"Price": (100, 100, 100), "Quality": (10, 10, 10)},
            "OptB": {"Price": (200, 200, 200), "Quality": (20, 20, 20)},
            "OptC": {"Price": (150, 150, 150), "Quality": (15, 15, 15)},
        }
        engine = TOPSISEngine()
        # Inverted: Previously asserted OptA > OptC > OptB under equal weights [0.5, 0.5]
        # due to asymmetric normalization (x / max_c for benefit vs min-max for cost, which
        # compressed the quality range to [0.5, 1.0] while price was [0.0, 1.0], implicitly
        # giving price twice the weight). With proper symmetric min-max normalization,
        # symmetric options have equal scores (0.5) under equal weights.
        scores_equal = engine.analyze(data, [0.5, 0.5], [False, True])
        assert len(scores_equal) == 3
        assert math.isclose(scores_equal["OptA"], 0.5)
        assert math.isclose(scores_equal["OptB"], 0.5)
        assert math.isclose(scores_equal["OptC"], 0.5)

        # When price is prioritized, OptA wins as expected:
        scores_price = engine.analyze(data, [0.7, 0.3], [False, True])
        assert scores_price["OptA"] > scores_price["OptC"] > scores_price["OptB"]


    def test_single_option(self):
        data = {"Only": {"X": (1, 2, 3)}}
        engine = TOPSISEngine()
        scores = engine.analyze(data, [1.0], [True])
        assert len(scores) == 1
        assert scores["Only"] == 1.0

    def test_empty_data(self):
        engine = TOPSISEngine()
        scores = engine.analyze({}, [1.0], [True])
        assert scores.empty

    def test_single_factor(self):
        data = {
            "A": {"Speed": (10, 20, 30)},
            "B": {"Speed": (20, 30, 40)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [1.0], [True])
        assert len(scores) == 2
        assert scores.index[0] == "B"

    def test_maximize_vs_minimize(self):
        data = {
            "A": {"Cost": (50, 50, 50), "Quality": (10, 10, 10)},
            "B": {"Cost": (100, 100, 100), "Quality": (5, 5, 5)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [0.5, 0.5], [False, True])
        assert len(scores) == 2

    def test_zero_weight_data(self):
        data = {
            "A": {"X": (1, 1, 1)},
            "B": {"X": (2, 2, 2)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [0.0], [True])
        assert len(scores) == 2
        assert scores.iloc[0] == scores.iloc[1]

    def test_identical_options_all_zero_scores(self):
        data = {
            "A": {"X": (10, 10, 10)},
            "B": {"X": (10, 10, 10)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [1.0], [True])
        assert scores["A"] == 0.0
        assert scores["B"] == 0.0

    def test_negative_weights(self):
        data = {
            "A": {"Cost": (100, 100, 100)},
            "B": {"Cost": (200, 200, 200)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [-0.5], [False])
        assert len(scores) == 2

    def test_mismatched_weights_length_warns(self):
        data = {
            "A": {"X": (1, 2, 3), "Y": (4, 5, 6)},
            "B": {"X": (2, 3, 4), "Y": (5, 6, 7)},
        }
        engine = TOPSISEngine()
        import pytest
        # Inverted: Previously logged a warning and truncated (crashing with IndexError if too few),
        # now raises ValueError when weights or maximize lengths do not match factor count.
        with pytest.raises(ValueError, match="Weights count"):
            engine.analyze(data, [1.0, 0.5, 0.5], [True, True])
        with pytest.raises(ValueError, match="Maximize count"):
            engine.analyze(data, [1.0, 0.5], [True])


    def test_partial_zero_weight_multi_factor(self):
        data = {
            "A": {"X": (1, 1, 1), "Y": (10, 10, 10)},
            "B": {"X": (2, 2, 2), "Y": (5, 5, 5)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [0.0, 1.0], [True, True])
        assert len(scores) == 2

    def test_negative_values_benefit_ranking_correct(self):
        """Negative values for benefit factors must not invert the ranking."""
        data = {
            "A": {"Profit": (-5.0, -5.0, -5.0)},
            "B": {"Profit": (-1.0, -1.0, -1.0)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [1.0], [True])
        # B (-1) is better than A (-5), so B must rank above A
        assert scores["B"] > scores["A"]

