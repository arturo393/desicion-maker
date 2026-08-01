import os
import tempfile

import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


class TestUnifiedDecisionFramework:
    @pytest.fixture
    def framework(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("Cost", 0.3, maximize=False))
        fw.add_factor(Factor("Benefit", 0.7, maximize=True))
        opt_a = DecisionOption("A", "Conservative")
        opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt_a.add_variable("Benefit", DistributionType.DETERMINISTIC, 100)
        fw.add_option(opt_a)
        opt_b = DecisionOption("B", "Aggressive")
        opt_b.add_variable("Cost", DistributionType.DETERMINISTIC, 80)
        opt_b.add_variable("Benefit", DistributionType.DETERMINISTIC, 200)
        fw.add_option(opt_b)
        return fw

    @pytest.mark.asyncio
    async def test_express_mode(self, framework):
        result = await framework.run_analysis(mode="express")
        assert "mc_results" in result
        assert "topsis_scores" in result
        assert "strategies" in result
        assert result["strategies"] == {}
        assert "files" in result

    @pytest.mark.asyncio
    async def test_standard_mode(self, framework):
        result = await framework.run_analysis(mode="standard")
        assert "strategies" in result
        assert len(result["strategies"]) > 0
        assert "promethee_uncertainty" in result["future"]
        assert "robust_optimizer" in result["future"]
        assert "rank_aggregation" in result["future"]
        assert "bayesian_probs" not in result["future"]

    @pytest.mark.asyncio
    async def test_advanced_mode(self, framework):
        result = await framework.run_analysis(mode="advanced")
        assert "future" in result
        assert "promethee_uncertainty" in result["future"]
        assert "robust_optimizer" in result["future"]
        assert "rank_aggregation" in result["future"]
        assert "bayesian_probs" in result["future"]
        assert "ideal_option" in result["future"]
        assert "promethee_scores" in result["future"]

    @pytest.mark.asyncio
    async def test_invalid_mode_falls_back(self, framework):
        result = await framework.run_analysis(mode="invalid")
        assert result["mode"] == "standard"
        assert "strategies" in result

    @pytest.mark.asyncio
    async def test_validation_warnings(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("Bad", 1.0, maximize=True))
        opt = DecisionOption("BadOpt")
        opt.add_variable("Bad", DistributionType.NORMAL, 0)
        fw.add_option(opt)

        result = await fw.run_analysis(mode="express")
        assert "mc_results" in result

    @pytest.mark.asyncio
    async def test_zero_options_returns_empty(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("X", 1.0, maximize=True))
        result = await fw.run_analysis(mode="express")
        assert result == {}

    @pytest.mark.asyncio
    async def test_zero_factors_returns_empty(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        opt = DecisionOption("Alone")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        fw.add_option(opt)
        result = await fw.run_analysis(mode="express")
        assert result == {}

    @pytest.mark.asyncio
    async def test_save_report_creates_files(self, framework):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await framework.run_analysis(
                mode="standard",
                results_dir=tmpdir,
            )
            files = result["files"]
            assert os.path.exists(files["json"])
            assert os.path.exists(files["md"])
            assert os.path.exists(files["html"])
