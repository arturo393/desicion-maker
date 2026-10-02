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

    def test_borda_unranked_options_receive_average_unassigned_points(self):
        """Options not ranked by a method must receive the average of unassigned points for that method."""
        rankings = {
            "M1": pd.Series([10, 5, 1], index=["A", "B", "C"]),
            "M2": pd.Series([10], index=["A"]),
        }
        # Total options = 3 (points available per method: 2, 1, 0)
        # M1: A=2, B=1, C=0
        # M2: A=2 (1st place). Unranked: B, C. Unassigned points: 1 and 0 -> avg = 0.5 each.
        # Total expected: A = 2 + 2 = 4.0, B = 1 + 0.5 = 1.5, C = 0 + 0.5 = 0.5
        result = RankAggregator.borda_count(rankings)
        assert result["A"] == 4.0
        assert result["B"] == 1.5
        assert result["C"] == 0.5
