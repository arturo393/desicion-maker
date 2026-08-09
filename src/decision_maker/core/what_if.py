"""
What-If interactive scenario runner for exploring factor weight and direction perturbations.
Usage: from decision_maker.core.what_if import WhatIfRunner
Does NOT: Export multi-page HTML reports or connect to external databases.
"""

from __future__ import annotations

__all__ = ["WhatIfEngine"]

import copy
import logging

import numpy as np

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


def _compute_raw_bounds(mc_results: dict[str, Statistics], factor_names: list) -> dict[str, dict[str, float]]:
    """Compute bounds using raw per-simulation data for accurate What-If ranges."""
    bounds: dict[str, dict[str, float]] = {fn: {"min": float("inf"), "max": float("-inf")} for fn in factor_names}
    for stats in mc_results.values():
        if stats.raw_factor_data is not None:
            for fn in factor_names:
                if fn in stats.raw_factor_data:
                    data = stats.raw_factor_data[fn]
                    bounds[fn]["min"] = min(bounds[fn]["min"], float(np.min(data)))
                    bounds[fn]["max"] = max(bounds[fn]["max"], float(np.max(data)))
        if stats.factor_stats is not None:
            for fn in factor_names:
                if fn in stats.factor_stats:
                    val = stats.factor_stats[fn]["mean"]
                    bounds[fn]["min"] = min(bounds[fn]["min"], val)
                    bounds[fn]["max"] = max(bounds[fn]["max"], val)
    return bounds


class WhatIfEngine:
    """
    Interactive What-If analysis engine.

    Takes MC results + factors, allows live weight/direction changes,
    and immediately recomputes scores to show the impact.

    Usage:
        engine = WhatIfEngine(mc_results, factors)
        engine.set_weight("Cost", 0.6)
        scores = engine.recompute()  # [(name, score), ...]
        engine.repl()                # full interactive session
    """

    def __init__(
        self,
        mc_results: dict[str, Statistics],
        factors: list[Factor],
    ):
        if not mc_results or not factors:
            raise ValueError("mc_results and factors must not be empty")

        self.original_mc_results = mc_results
        self.original_factors = [Factor(f.name, f.weight, f.maximize, f.category) for f in factors]
        self.current_factors = [Factor(f.name, f.weight, f.maximize, f.category) for f in factors]
        self._global_bounds = _compute_raw_bounds(self.original_mc_results, [f.name for f in self.original_factors])

    # ── Public mutation API ──────────────────────────────────────────

    def assign_weight(self, factor_name: str, weight: float) -> bool:
        """Set a factor's weight. Returns True if found, False otherwise."""
        for f in self.current_factors:
            if f.name == factor_name:
                f.weight = float(weight)
                return True
        return False

    def toggle_maximize(self, factor_name: str) -> bool | None:
        """Toggle maximize/minimize. Returns new value or None if not found."""
        for f in self.current_factors:
            if f.name == factor_name:
                f.maximize = not f.maximize
                return f.maximize
        return None

    def assign_all_weights(self, weights: dict[str, float]) -> list[str]:
        """Set multiple weights at once. Returns list of names not found."""
        not_found = []
        for name, w in weights.items():
            if not self.assign_weight(name, w):
                not_found.append(name)
        return not_found

    def reset(self) -> None:
        """Restore original factor weights and directions."""
        self.current_factors = copy.deepcopy(self.original_factors)

    # ── Recomputation ────────────────────────────────────────────────

    def recompute(self) -> list[tuple[str, float]]:
        """
        Recompute scores with current factor settings.

        Uses raw_factor_data when available (exact per-simulation
        recomputation), otherwise falls back to factor_stats means
        (deterministic approximation).

        Returns: [(option_name, score), ...] sorted descending by score.
        """
        results: dict[str, float] = {}

        for opt_name, stats in self.original_mc_results.items():
            # Prefer raw per-simulation data
            if stats.raw_factor_data is not None:
                raw_data = stats.raw_factor_data
            else:
                raw_data = {fn: np.array([fstats["mean"]]) for fn, fstats in stats.factor_stats.items()}

            total_scores: np.ndarray | None = None

            for f in self.current_factors:
                if f.name not in raw_data:
                    continue

                raw_values = raw_data[f.name]
                bounds = self._global_bounds.get(f.name, {"min": 0.0, "max": 1.0})
                f_min, f_max = bounds["min"], bounds["max"]

                norm_values = (raw_values - f_min) / (f_max - f_min) if f_max > f_min else np.full_like(raw_values, 1.0)

                weighted = norm_values * f.weight if f.maximize else (1.0 - norm_values) * f.weight

                total_scores = weighted.copy() if total_scores is None else total_scores + weighted

            if total_scores is None:
                continue

            results[opt_name] = float(np.mean(total_scores))

        return sorted(results.items(), key=lambda x: x[1], reverse=True)

    def recompute_with_weights(self, weights: dict[str, float]) -> list[tuple[str, float]]:
        """
        Convenience: set weights, recompute, restore previous state.

        Returns same as recompute() without permanently changing state.
        """
        saved = {f.name: f.weight for f in self.current_factors}
        self.assign_all_weights(weights)
        scores = self.recompute()
        for f in self.current_factors:
            if f.name in saved:
                f.weight = saved[f.name]
        return scores

    # ── Introspection ────────────────────────────────────────────────

    def diff(self) -> list[str]:
        """List changes between current and original configuration."""
        changes = []
        original_map = {f.name: f for f in self.original_factors}
        for cf in self.current_factors:
            of = original_map.get(cf.name)
            if of is None:
                continue
            if abs(cf.weight - of.weight) > 1e-9:
                changes.append(f"{cf.name}: weight {of.weight:.2f} -> {cf.weight:.2f}")
            if cf.maximize != of.maximize:
                direction = "maximize" if cf.maximize else "minimize"
                changes.append(f"{cf.name}: direction -> {direction}")
        return changes

    def original_ranking(self) -> list[tuple[str, float]]:
        """Return the original ranking from mc_results."""
        sorted_opts = sorted(
            self.original_mc_results.items(),
            key=lambda x: x[1].mean_score,
            reverse=True,
        )
        return [(name, stats.mean_score) for name, stats in sorted_opts]

    # ── Pretty printing ──────────────────────────────────────────────

    @staticmethod
    def summary_table(scores: list[tuple[str, float]]) -> str:
        """Pretty-print ranking table."""
        if not scores:
            return "No results."
        lines = [
            f"{'Rank':<6} {'Option':<35} {'Score':<10}",
            "-" * 51,
        ]
        for i, (name, score) in enumerate(scores, 1):
            marker = " ★" if i == 1 else ""
            lines.append(f"{i:<6} {name:<35} {score:<10.4f}{marker}")
        return "\n".join(lines)

    @staticmethod
    def factor_table(factors: list[Factor]) -> str:
        """Pretty-print factor configuration."""
        lines = [
            f"{'Factor':<25} {'Weight':<8} {'Direction':<12}",
            "-" * 45,
        ]
        for f in factors:
            direction = "↑ max" if f.maximize else "↓ min"
            lines.append(f"{f.name:<25} {f.weight:<8.2f} {direction:<12}")
        return "\n".join(lines)

    @staticmethod
    def comparison_table(
        original: list[tuple[str, float]],
        current: list[tuple[str, float]],
    ) -> str:
        """Show side-by-side comparison of original vs current rankings."""
        orig_map = {name: score for name, score in original}
        cur_map = {name: score for name, score in current}
        all_names = list(dict.fromkeys([n for n, _ in original] + [n for n, _ in current]))

        lines = [
            f"{'Rank':<6} {'Option':<35} {'Before':<10} {'After':<10} {'Δ':<10}",
            "-" * 71,
        ]
        for i, name in enumerate(all_names, 1):
            before = orig_map.get(name, 0.0)
            after = cur_map.get(name, 0.0)
            delta = after - before
            delta_str = f"{delta:+.4f}" if abs(delta) > 1e-6 else ""
            marker = " ★" if i == 1 else ""
            lines.append(f"{i:<6} {name:<35} {before:<10.4f} {after:<10.4f} {delta_str:<10}{marker}")
        return "\n".join(lines)

    # ── REPL ─────────────────────────────────────────────────────────

    def repl(self) -> None:
        """Interactive What-If REPL — explore weight changes live."""
        print("\n" + "=" * 64)
        print("  WHAT-IF ANALYSIS MODE")
        print("  Adjust factor weights and directions to see how rankings change.")
        print("  Type 'help' for commands, 'quit' to exit.")
        print("=" * 64)

        self._show_initial()

        while True:
            try:
                raw = input("\nwhat-if> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                break
            elif cmd in ("help", "?"):
                self._show_help()
            elif cmd == "show":
                scores = self.recompute()
                print(self.summary_table(scores))
            elif cmd in ("factors", "factor"):
                print(self.factor_table(self.current_factors))
            elif cmd == "diff":
                changes = self.diff()
                if changes:
                    print("Changes from original:")
                    for c in changes:
                        print(f"  • {c}")
                else:
                    print("No changes from original configuration")
            elif cmd == "reset":
                self.reset()
                print("Reset to original weights and directions")
            elif cmd == "weight" and len(parts) >= 3:
                fname = parts[1]
                try:
                    w = float(parts[2])
                    if self.assign_weight(fname, w):
                        scores = self.recompute()
                        print(f"Set {fname} weight to {w:.2f}")
                        print(self.summary_table(scores))
                    else:
                        available = [f.name for f in self.current_factors]
                        print(f"Unknown factor: {fname}. Available: {available}")
                except ValueError:
                    print(f"Invalid weight: {parts[2]}")
            elif cmd == "toggle" and len(parts) >= 2:
                fname = parts[1]
                result = self.toggle_maximize(fname)
                if result is not None:
                    direction = "maximize" if result else "minimize"
                    scores = self.recompute()
                    print(f"Toggled {fname} to {direction}")
                    print(self.summary_table(scores))
                else:
                    available = [f.name for f in self.current_factors]
                    print(f"Unknown factor: {fname}. Available: {available}")
            elif cmd == "compare":
                original = self.original_ranking()
                current = self.recompute()
                print(self.comparison_table(original, current))
            elif cmd == "try":
                if len(parts) < 2:
                    print("Usage: try <name1>=<w1> <name2>=<w2> ...")
                    continue
                weights = {}
                for part in parts[1:]:
                    if "=" in part:
                        fname, wstr = part.split("=", 1)
                        try:
                            weights[fname.strip()] = float(wstr.strip())
                        except ValueError:
                            print(f"Invalid weight in '{part}'")
                    else:
                        print(f"Expected name=weight format, got '{part}'")
                if weights:
                    saved = {f.name: f.weight for f in self.current_factors}
                    self.assign_all_weights(weights)
                    scores = self.recompute()
                    print("Temporary weights applied:")
                    print(self.summary_table(scores))
                    print("\nWhat changed?")
                    for c in self.diff():
                        print(f"  • {c}")
                    for f in self.current_factors:
                        if f.name in saved:
                            f.weight = saved[f.name]
                    print("(weights restored)")
            elif cmd == "suggest":
                suggestions = self._suggest()
                if suggestions:
                    print("Suggestions — factors whose weight sensitivity could flip rankings:")
                    for s in suggestions:
                        print(f"  • {s}")
                else:
                    print("No sensitivity-driven suggestions found.")
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")

        self._show_final()

    def _suggest(self) -> list[str]:
        scores = self.recompute()
        if len(scores) < 2:
            return []
        winner_name, winner_score = scores[0]
        winner_stats = self.original_mc_results.get(winner_name)
        suggestions = []
        for name, score in scores[1:]:
            gap = winner_score - score
            stats = self.original_mc_results.get(name)
            if not stats or not winner_stats:
                continue
            for f in self.current_factors:
                if f.name not in stats.factor_stats or f.name not in winner_stats.factor_stats:
                    continue
                raw_mean = stats.factor_stats[f.name]["mean"]
                winner_raw = winner_stats.factor_stats[f.name]["mean"]
                bounds = self._global_bounds.get(f.name, {"min": 0, "max": 1})
                f_min, f_max = bounds["min"], bounds["max"]
                if f_max > f_min:
                    norm_val = (raw_mean - f_min) / (f_max - f_min)
                    winner_norm = (winner_raw - f_min) / (f_max - f_min)
                else:
                    norm_val = 1.0
                    winner_norm = 1.0
                effective = norm_val if f.maximize else (1.0 - norm_val)
                winner_effective = winner_norm if f.maximize else (1.0 - winner_norm)
                delta_per_unit = winner_effective - effective
                if delta_per_unit < 0 and effective > 0:
                    extra = gap / (-delta_per_unit)
                    pct = (extra / f.weight) * 100 if f.weight > 0 else 0
                    if abs(pct) < 200:
                        suggestions.append(
                            f"  {name} could beat {winner_name} if {f.name} weight "
                            f"changed by {pct:+.0f}% (to {f.weight + extra:.2f})"
                        )
        return suggestions

    def _show_initial(self) -> None:
        print("\nCurrent factors:")
        print(self.factor_table(self.current_factors))
        print("\nOriginal ranking:")
        print(self.summary_table(self.original_ranking()))

    def _show_final(self) -> None:
        original = self.original_ranking()
        current = self.recompute()
        print("\n" + "=" * 64)
        print("  FINAL WHAT-IF SUMMARY")
        print("=" * 64)
        print("\nComparison (before → after):")
        print(self.comparison_table(original, current))
        print("\nFactors:")
        print(self.factor_table(self.current_factors))
        changes = self.diff()
        if changes:
            print("What changed:")
            for c in changes:
                print(f"  • {c}")
        print("=" * 64)

    def _show_help(self) -> None:
        print(
            """
Commands:
  show                           Show current rankings
  factors                        Show factor weights and directions
  weight <name> <value>          Set a factor's weight and show new ranking
  toggle <name>                  Toggle maximize/minimize for a factor
  try <n1>=<w1> <n2>=<w2> ...   Try temporary weights (non-destructive)
  compare                        Side-by-side before vs after comparison
  suggest                        Show sensitivity-based weight suggestions
  diff                           List changes from original configuration
  reset                          Restore original weights and directions
  help, ?                        Show this help
  quit, exit, q                  Exit what-if mode
"""
        )
