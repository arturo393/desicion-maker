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
        from pydantic import ValidationError
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("Bad", 1.0, maximize=True))
        opt = DecisionOption("BadOpt")

        with pytest.raises(ValidationError):
            opt.add_variable("Bad", DistributionType.NORMAL, 0)

    @pytest.mark.asyncio
    async def test_zero_options_raises(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("X", 1.0, maximize=True))
        with pytest.raises(ValueError, match="no options"):
            await fw.run_analysis(mode="express")

    @pytest.mark.asyncio
    async def test_zero_factors_raises(self):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        opt = DecisionOption("Alone")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        fw.add_option(opt)
        with pytest.raises(ValueError, match="no factors"):
            await fw.run_analysis(mode="express")

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

    @pytest.mark.asyncio
    async def test_vetoed_options_excluded_from_subsequent_rankings(self, monkeypatch):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 100
        fw.add_factor(Factor("Cost", 0.5, maximize=False))
        fw.add_factor(Factor("Benefit", 0.5, maximize=True))

        opt_a = DecisionOption("A", "Good Option")
        opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt_a.add_variable("Benefit", DistributionType.DETERMINISTIC, 100)
        fw.add_option(opt_a)

        opt_b = DecisionOption("B", "Bad Option to Veto")
        opt_b.add_variable("Cost", DistributionType.DETERMINISTIC, 100)
        opt_b.add_variable("Benefit", DistributionType.DETERMINISTIC, 10)
        fw.add_option(opt_b)

        original_apply = fw.decision_gates.apply

        def mock_apply(*args, **kwargs):
            res = original_apply(*args, **kwargs)
            if "B" in res.options_approved:
                res.options_approved.remove("B")
            if "B" not in res.options_vetoed:
                res.options_vetoed.append("B")
                res.veto_count += 1
            return res

        monkeypatch.setattr(fw.decision_gates, "apply", mock_apply)

        result = await fw.run_analysis(mode="standard")

        assert "B" in result["gate_result"]["options_vetoed"]
        assert "B" not in result["topsis_scores"].index
        assert "B" not in result["future"]["rank_aggregation"]["ranking"]
        assert "B" not in result["future"]["rank_aggregation"]["scores"]


    @pytest.mark.asyncio
    async def test_winner_agreement_structure(self, framework):
        result = await framework.run_analysis(mode="standard")
        assert "winner_agreement" in result
        agreement = result["winner_agreement"]
        assert isinstance(agreement, dict)
        assert "topsis" in agreement
        assert isinstance(agreement["topsis"], bool)
        assert "borda" in agreement
        assert isinstance(agreement["borda"], bool)

    @pytest.mark.asyncio
    async def test_advanced_mode_promethee_crisp_is_normalized(self, monkeypatch):
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 50
        fw.add_factor(Factor("F1", 0.5, maximize=True))
        fw.add_factor(Factor("F2", 0.5, maximize=True))

        opt_a = DecisionOption("A")
        opt_a.add_variable("F1", DistributionType.DETERMINISTIC, 100.0)
        opt_a.add_variable("F2", DistributionType.DETERMINISTIC, 500.0)
        fw.add_option(opt_a)

        opt_b = DecisionOption("B")
        opt_b.add_variable("F1", DistributionType.DETERMINISTIC, 200.0)
        opt_b.add_variable("F2", DistributionType.DETERMINISTIC, 600.0)
        fw.add_option(opt_b)

        captured_dfs = []
        original_promethee_analyze = fw.promethee_engine.analyze

        def spy_analyze(df, config):
            captured_dfs.append(df.copy())
            return original_promethee_analyze(df, config)

        monkeypatch.setattr(fw.promethee_engine, "analyze", spy_analyze)

        await fw.run_analysis(mode="advanced")

        # The crisp promethee call should have received a normalized dataframe where values are in [0, 1]
        assert len(captured_dfs) > 0
        crisp_df = captured_dfs[-1]  # crisp is analyzed in _run_advanced_analysis
        assert ((crisp_df >= 0.0) & (crisp_df <= 1.0)).all().all()


