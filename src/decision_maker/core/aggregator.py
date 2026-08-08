"""
Aggregates rank orders from multiple decision algorithms using Borda and Copeland methods.
Usage: from decision_maker.core.aggregator import RankAggregator
Does NOT: Compute raw statistical scores or run Monte Carlo simulations directly.
"""

from __future__ import annotations

__all__ = ["RankAggregator"]

from typing import Any

import pandas as pd


class RankAggregator:
    @staticmethod
    def borda_count(rankings: dict[str, pd.Series]) -> pd.Series:
        if not rankings:
            return pd.Series()
        all_options = set()
        for series in rankings.values():
            all_options.update(series.index)
        all_options = sorted(all_options)
        n = len(all_options)
        borda_scores = {opt: 0.0 for opt in all_options}
        for method_name, series in rankings.items():
            ranked = series.index.tolist()
            for rank_pos, opt in enumerate(ranked):
                borda_scores[opt] += n - rank_pos - 1
        return pd.Series(borda_scores).sort_values(ascending=False)

    @staticmethod
    def copeland(rankings: dict[str, pd.Series]) -> pd.Series:
        if not rankings:
            return pd.Series()
        all_options = set()
        for series in rankings.values():
            all_options.update(series.index)
        all_options = sorted(all_options)
        copeland_scores = {opt: 0.0 for opt in all_options}
        for a in all_options:
            for b in all_options:
                if a >= b:
                    continue
                wins_a = 0
                wins_b = 0
                for method_name, series in rankings.items():
                    pos_a = series.index.get_indexer([a])[0]
                    if pos_a < 0:
                        pos_a = len(series)
                    pos_b = series.index.get_indexer([b])[0]
                    if pos_b < 0:
                        pos_b = len(series)
                    if pos_a < pos_b:
                        wins_a += 1
                    elif pos_b < pos_a:
                        wins_b += 1
                if wins_a > wins_b:
                    copeland_scores[a] += 1
                elif wins_b > wins_a:
                    copeland_scores[b] += 1
                else:
                    copeland_scores[a] += 0.5
                    copeland_scores[b] += 0.5
        return pd.Series(copeland_scores).sort_values(ascending=False)

    @staticmethod
    def aggregate(
        rankings: dict[str, pd.Series],
        method: str = "borda",
    ) -> dict[str, Any]:
        if method == "borda":
            result = RankAggregator.borda_count(rankings)
        elif method == "copeland":
            result = RankAggregator.copeland(rankings)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        return {
            "method": method,
            "scores": result.to_dict(),
            "winner": result.index[0] if not result.empty else None,
            "ranking": result.index.tolist(),
        }
