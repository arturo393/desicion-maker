"""
Game Theory Engine.
Calculates Nash Equilibrium strategies given a payoff matrix for multi-agent dynamic markets.
"""


import numpy as np


class GameTheoryEngine:
    def __init__(self):
        pass

    def find_pure_nash_equilibria(self, payoff_matrix: np.ndarray) -> list[tuple[int, int]]:
        """
        Finds pure strategy Nash Equilibria for a 2-player bimatrix game.
        payoff_matrix shape: (num_actions_p1, num_actions_p2, 2)
        """
        equilibria = []
        rows, cols, _ = payoff_matrix.shape

        # Best responses for Player 1 (Rows) given Player 2 (Cols)
        p1_best_responses = np.zeros((rows, cols), dtype=bool)
        for j in range(cols):
            max_payoff = np.max(payoff_matrix[:, j, 0])
            for i in range(rows):
                if payoff_matrix[i, j, 0] == max_payoff:
                    p1_best_responses[i, j] = True

        # Best responses for Player 2 (Cols) given Player 1 (Rows)
        p2_best_responses = np.zeros((rows, cols), dtype=bool)
        for i in range(rows):
            max_payoff = np.max(payoff_matrix[i, :, 1])
            for j in range(cols):
                if payoff_matrix[i, j, 1] == max_payoff:
                    p2_best_responses[i, j] = True

        # Nash Equilibria are intersections of best responses
        for i in range(rows):
            for j in range(cols):
                if p1_best_responses[i, j] and p2_best_responses[i, j]:
                    equilibria.append((i, j))

        return equilibria

    def analyze(self, mc_results: dict) -> dict[str, str]:
        """
        Simulates a game against a hypothetical competitor.
        Returns a string categorization of the option's robustness in a Nash Equilibrium.
        """
        option_names = list(mc_results.keys())
        if not option_names:
            return {}

        results = {}
        # In a real scenario, the matrix would be dynamically built.
        # Here we simulate a 2x2 competitive interaction based on stats.
        for name, stats in mc_results.items():
            base_val = stats.mean_score
            # Option payoff against aggressive vs passive competitor
            matrix = np.array([
                [[base_val * 0.8, base_val * 1.2], [base_val * 1.1, base_val * 0.9]],
                [[base_val * 0.9, base_val * 1.1], [base_val * 1.0, base_val * 1.0]]
            ])

            eqs = self.find_pure_nash_equilibria(matrix)
            if eqs:
                results[name] = f"Stable in {len(eqs)} pure Nash Equilibrium(s)"
            else:
                results[name] = "Requires Mixed Strategy (No pure Nash Equilibrium)"

        return results
