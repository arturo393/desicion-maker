import pandas as pd
import pytest

from decision_maker.core.aggregator import RankAggregator


class TestRankAggregator:
    def test_borda_count_basic(self):
        rankings = {
            "TOPSIS": pd.Series([1, 2, 3], index=["A", "B", "C"]),
            "PROMETHEE": pd.Series([2, 1, 3], index=["B", "A", "C"]),
        }
        result = RankAggregator.aggregate(rankings, method="borda")
        assert result["winner"] is not None

    def test_borda_finds_consensus(self):
        rankings = {
            "A": pd.Series([1, 2, 3], index=["X", "Y", "Z"]),
            "B": pd.Series([1, 2, 3], index=["X", "Y", "Z"]),
            "C": pd.Series([1, 2, 3], index=["X", "Y", "Z"]),
        }
        result = RankAggregator.aggregate(rankings, method="borda")
        assert result["winner"] == "X"

    def test_copeland_basic(self):
        rankings = {
            "A": pd.Series([1, 2], index=["X", "Y"]),
            "B": pd.Series([2, 1], index=["Y", "X"]),
        }
        result = RankAggregator.aggregate(rankings, method="copeland")
        assert result["winner"] is not None

    def test_empty_rankings(self):
        result = RankAggregator.aggregate({}, method="borda")
        assert result["winner"] is None
        assert result["scores"] == {}

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match=".*"):
            RankAggregator.aggregate({"A": pd.Series([1], index=["X"])}, method="unknown")

    def test_borda_count_empty_series(self):
        result = RankAggregator.borda_count({})
        assert result.empty

    def test_copeland_empty_series(self):
        result = RankAggregator.copeland({})
        assert result.empty
