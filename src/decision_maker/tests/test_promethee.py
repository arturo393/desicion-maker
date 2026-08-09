import pandas as pd

from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine


class TestPrometheeEngine:
    def test_basic_ranking(self):
        df = pd.DataFrame(
            {"Cost": [100, 200, 150], "Quality": [10, 20, 15]},
            index=["A", "B", "C"],
        )
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[0.5, 0.5], maximize=[False, True]))
        assert len(scores) == 3

    def test_single_option(self):
        df = pd.DataFrame({"Cost": [100]}, index=["Only"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[False]))
        assert len(scores) == 1
        assert scores.iloc[0] == 0.0

    def test_no_columns_returns_empty(self):
        df = pd.DataFrame(index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[], maximize=[]))
        assert scores.empty

    def test_two_options(self):
        df = pd.DataFrame({"X": [10, 20]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[True]))
        assert scores.index[0] == "B"

    def test_all_minimize(self):
        df = pd.DataFrame({"Cost": [100, 50]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[False]))
        assert scores.index[0] == "B"

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[True]))
        assert scores.empty

    def test_equal_options(self):
        df = pd.DataFrame({"X": [10, 10]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[True]))
        assert len(scores) == 2
        assert scores.iloc[0] == scores.iloc[1]

    def test_nan_values_handled(self):
        df = pd.DataFrame({"X": [10, float("nan")]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[True]))
        assert len(scores) == 2

    def test_all_weights_zero(self):
        df = pd.DataFrame({"X": [10, 20]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[0.0, 0.0], maximize=[True, True]))
        assert scores["A"] == scores["B"] == 0.0

    def test_pref_type_usual(self):
        df = pd.DataFrame({"X": [10, 20]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["usual"]))
        assert scores.index[0] == "B"

    def test_pref_type_ushape_with_q(self):
        df = pd.DataFrame({"X": [10, 15]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores_no_pref = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["ushape"], pref_params=[{"q": 10}])
        )
        scores_pref = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["ushape"], pref_params=[{"q": 3}])
        )
        assert scores_no_pref["A"] == scores_no_pref["B"]
        assert scores_pref.index[0] == "B"

    def test_pref_type_vshape(self):
        df = pd.DataFrame({"X": [0, 10]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["vshape"], pref_params=[{"p": 20}])
        )
        assert 0 < scores["B"] < 1.0

    def test_pref_type_linear(self):
        df = pd.DataFrame({"X": [0, 10]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["linear"], pref_params=[{"q": 2, "p": 20}])
        )
        assert 0 < scores["B"] < 1.0

    def test_pref_type_level(self):
        df = pd.DataFrame({"X": [0, 10]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["level"], pref_params=[{"q": 5, "p": 15}])
        )
        assert scores["B"] == 0.5

    def test_pref_type_gaussian(self):
        df = pd.DataFrame({"X": [0, 3]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(
            df, PrometheeConfig(weights=[1.0], maximize=[True], pref_types=["gaussian"], pref_params=[{"s": 2}])
        )
        assert 0 < scores["B"] < 1.0

    def test_custom_pref_types_per_factor(self):
        df = pd.DataFrame({"Cost": [100, 200], "Quality": [10, 20]}, index=["A", "B"])
        engine = PrometheeEngine()
        scores = engine.analyze(
            df,
            PrometheeConfig(
                weights=[0.5, 0.5],
                maximize=[False, True],
                pref_types=["linear", "gaussian"],
                pref_params=[{"q": 50, "p": 150}, {"s": 5}],
            ),
        )
        assert len(scores) == 2

    def test_dataframe_no_columns(self):
        df = pd.DataFrame({"A": [], "B": []})
        engine = PrometheeEngine()
        scores = engine.analyze(df, PrometheeConfig(weights=[], maximize=[]))
        assert scores.empty
