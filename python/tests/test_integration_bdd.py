import pytest

from python.core.models import DecisionOption, DistributionType, Factor
from python.core.orchestrator import UnifiedDecisionFramework


@pytest.mark.asyncio
class TestDecisionWorkflowBDD:
    async def test_given_factors_and_options_when_express_mode_then_basic_results_returned(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 1000
        fw.add_factor(Factor("Cost", 0.3, maximize=False))
        fw.add_factor(Factor("Quality", 0.7, maximize=True))

        cheap = DecisionOption("Cheap", "Low cost option")
        cheap.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        cheap.add_variable("Quality", DistributionType.DETERMINISTIC, 60)
        fw.add_option(cheap)

        premium = DecisionOption("Premium", "High quality option")
        premium.add_variable("Cost", DistributionType.DETERMINISTIC, 100)
        premium.add_variable("Quality", DistributionType.DETERMINISTIC, 90)
        fw.add_option(premium)

        result = await fw.run_analysis(mode="express")

        assert "mc_results" in result
        assert "topsis_scores" in result
        assert "strategies" in result
        assert "pareto" in result
        assert result["strategies"] == {}
        assert len(result["mc_results"]) == 2
        assert len(result["topsis_scores"]) == 2

    async def test_given_factors_and_options_when_standard_mode_then_decision_strategies_included(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 1000
        fw.add_factor(Factor("Cost", 0.3, maximize=False))
        fw.add_factor(Factor("Quality", 0.7, maximize=True))

        a = DecisionOption("A")
        a.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        a.add_variable("Quality", DistributionType.DETERMINISTIC, 60)
        fw.add_option(a)

        b = DecisionOption("B")
        b.add_variable("Cost", DistributionType.DETERMINISTIC, 100)
        b.add_variable("Quality", DistributionType.DETERMINISTIC, 90)
        fw.add_option(b)

        result = await fw.run_analysis(mode="standard")

        assert len(result["strategies"]) > 0
        assert "Maximax (Optimistic)" in result["strategies"]
        assert "sensitivity" in result
        assert "promethee_uncertainty" in result["future"]
        assert "robust_optimizer" in result["future"]
        assert "rank_aggregation" in result["future"]
        assert "bayesian_probs" not in result["future"]
        assert "ideal_option" not in result["future"]

    async def test_given_factors_and_options_when_advanced_mode_then_bayesian_and_genetic_included(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 1000
        fw.add_factor(Factor("Cost", 0.3, maximize=False))
        fw.add_factor(Factor("Quality", 0.7, maximize=True))

        a = DecisionOption("A")
        a.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        a.add_variable("Quality", DistributionType.DETERMINISTIC, 60)
        fw.add_option(a)

        b = DecisionOption("B")
        b.add_variable("Cost", DistributionType.DETERMINISTIC, 100)
        b.add_variable("Quality", DistributionType.DETERMINISTIC, 90)
        fw.add_option(b)

        result = await fw.run_analysis(mode="advanced")

        assert "bayesian_probs" in result["future"]
        assert "ideal_option" in result["future"]
        assert "promethee_scores" in result["future"]

    async def test_given_no_options_when_run_then_no_results_returned(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("X", 1.0, maximize=True))

        result = await fw.run_analysis(mode="express")

        assert result == {}

    async def test_given_no_factors_when_run_then_no_results_returned(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        fw.add_option(opt)

        result = await fw.run_analysis(mode="express")

        assert result == {}

    async def test_given_single_option_when_run_then_results_returned(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("X", 1.0, maximize=True))
        opt = DecisionOption("Only")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        fw.add_option(opt)

        result = await fw.run_analysis(mode="express")

        assert result["mc_results"]["Only"].mean_score == 42.0
        assert result["topsis_scores"]["Only"] == 1.0

    async def test_given_uncertain_variables_when_advanced_mode_then_all_engines_run(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 5000
        fw.add_factor(Factor("Return", 0.6, maximize=True))
        fw.add_factor(Factor("Risk", 0.4, maximize=False))

        safe = DecisionOption("Safe", "Low risk")
        safe.add_variable("Return", DistributionType.NORMAL, 5, 2)
        safe.add_variable("Risk", DistributionType.NORMAL, 10, 3)
        fw.add_option(safe)

        risky = DecisionOption("Risky", "High risk high reward")
        risky.add_variable("Return", DistributionType.NORMAL, 15, 10)
        risky.add_variable("Risk", DistributionType.NORMAL, 30, 15)
        fw.add_option(risky)

        result = await fw.run_analysis(mode="advanced")

        mc = result["mc_results"]
        assert "Safe" in mc
        assert "Risky" in mc
        assert result["topsis_scores"]["Risky"] > result["topsis_scores"]["Safe"]

        ideal = result["future"]["ideal_option"]
        assert ideal["raw_max"] > 0

        bayes = result["future"]["bayesian_probs"]
        assert 0 <= bayes["Safe"] <= 1
        assert 0 <= bayes["Risky"] <= 1
