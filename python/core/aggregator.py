from __future__ import annotations

__all__ = ["RankAggregator"]

from typing import Any, Dict, List

import pandas as pd


class RankAggregator:
    @staticmethod
    def borda_count(rankings: Dict[str, pd.Series]) -> pd.Series:
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
    def copeland(rankings: Dict[str, pd.Series]) -> pd.Series:
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
                    pos_a = series.index.get_loc(a) if a in series.index else len(series)
                    pos_b = series.index.get_loc(b) if b in series.index else len(series)
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
        rankings: Dict[str, pd.Series],
        method: str = "borda",
    ) -> Dict[str, Any]:
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
