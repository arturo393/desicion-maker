"""
Machine Learning Surrogate Model Engine.
Trains lightweight Neural/Tree surrogates to predict fitness in microsecond latency,
bypassing expensive full Monte Carlo evaluation for genetic optimization passes.
"""

from typing import Any

from sklearn.ensemble import RandomForestRegressor

from decision_maker.core.models import Factor


class MLSurrogateEngine:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        self.feature_names = []

    def train(self, mc_results: dict, factors: list[Factor]) -> None:
        """
        Trains the surrogate model on the Monte Carlo results dataset.
        X = Factor Means
        Y = Option Mean Score
        """
        self.feature_names = [f.name for f in factors]
        X = []
        y = []

        for _name, stats in mc_results.items():
            features = []
            for fname in self.feature_names:
                if fname in stats.factor_stats:
                    features.append(stats.factor_stats[fname]["mean"])
                else:
                    features.append(0.0)
            X.append(features)
            y.append(stats.mean_score)

        if len(X) >= 2: # Need minimum samples to train
            self.model.fit(X, y)
            self.is_trained = True

    def predict_fitness(self, factor_values: list[float]) -> float:
        """
        Microsecond-latency fitness prediction.
        """
        if not self.is_trained:
            return sum(factor_values) # fallback

        prediction = self.model.predict([factor_values])
        return float(prediction[0])

    def analyze(self, mc_results: dict, factors: list[Factor]) -> dict[str, Any]:
        self.train(mc_results, factors)
        if not self.is_trained:
            return {"status": "Insufficient data to train ML Surrogate"}

        # Test self-prediction accuracy
        mse = 0.0
        for _name, stats in mc_results.items():
            f_vals = [stats.factor_stats.get(f.name, {}).get("mean", 0.0) for f in factors]
            pred = self.predict_fitness(f_vals)
            mse += (pred - stats.mean_score) ** 2

        mse /= len(mc_results)

        return {
            "status": "Trained successfully",
            "features": self.feature_names,
            "mse": mse
        }
