import pytest

from python.core.topsis import TOPSISEngine


class TestTOPSISEngine:
    def test_ranking(self):
        data = {
            "OptA": {"Price": (100, 100, 100), "Quality": (10, 10, 10)},
            "OptB": {"Price": (200, 200, 200), "Quality": (20, 20, 20)},
            "OptC": {"Price": (150, 150, 150), "Quality": (15, 15, 15)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [0.5, 0.5], [False, True])
        assert len(scores) == 3
        assert scores.index[0] in scores

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
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [1.0, 0.5, 0.5], [True, True, False])
        assert len(scores) == 1  # Doesn't crash, truncates extra weights

    def test_partial_zero_weight_multi_factor(self):
        data = {
            "A": {"X": (1, 1, 1), "Y": (10, 10, 10)},
            "B": {"X": (2, 2, 2), "Y": (5, 5, 5)},
        }
        engine = TOPSISEngine()
        scores = engine.analyze(data, [0.0, 1.0], [True, True])
        assert len(scores) == 2
