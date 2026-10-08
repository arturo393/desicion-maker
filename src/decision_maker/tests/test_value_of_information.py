"""
Tests for Value of Information (VoI): EVPI and EVPPI by risk driver.

Verifies:
1. Hand-calculable case with exact analytical EVPI and EVPPI values.
2. Dominant option in all scenarios produces EVPI = 0.0.
3. Unshared model returns EVPI = None with explicit noise explanation.
4. Axiomatic property: EVPI >= 0 and EVPPI(driver) <= EVPI.
5. EVPPI ranking sorts drivers in descending order of value.
6. VoI integration through orchestrator result dictionary.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics
from decision_maker.core.value_of_information import calculate_value_of_information

TOLERANCE: float = 1e-6


class TestValueOfInformation:
    def test_hand_calculated_evpi_and_evppi_exact_match(self) -> None:
        """Hand-calculable analytical scenario with exact EVPI and EVPPI values.

        Setup:
            N = 2000 simulations.
            First 1000 draws (low state): Option A = 10.0, Option B = 30.0. Winner is B (30.0).
            Last 1000 draws (high state): Option A = 40.0, Option B = 20.0. Winner is A (40.0).

        Hand calculation:
            Prior mean A = (1000 * 10 + 1000 * 40) / 2000 = 25.0
            Prior mean B = (1000 * 30 + 1000 * 20) / 2000 = 25.0
            Prior baseline expected payoff = max(25.0, 25.0) = 25.0
            Winner option = A (or B, both equal 25.0)

            With perfect information:
                In low state (50% prob): choose B for payoff 30.0
                In high state (50% prob): choose A for payoff 40.0
                Expected payoff = 0.5 * 30.0 + 0.5 * 40.0 = 35.0

            Exact EVPI = 35.0 - 25.0 = 10.0
            Exact EVPI fraction = 10.0 / 25.0 = 0.40 (40.0%)
            Exact EVPPI(driver) = 10.0 (knowing this driver reveals the high/low state)
        """
        driver_vals = np.concatenate([np.full(1000, 0.25), np.full(1000, 0.75)])
        scores_a = np.concatenate([np.full(1000, 10.0), np.full(1000, 40.0)])
        scores_b = np.concatenate([np.full(1000, 30.0), np.full(1000, 20.0)])

        results = {
            "Option_A": Statistics(
                "Option_A", 25.0, 15.0, 10.0, 40.0, 10.0, 40.0, 0.5, {}, 10.0, 10.0,
                raw_scores=scores_a,
            ),
            "Option_B": Statistics(
                "Option_B", 25.0, 5.0, 20.0, 30.0, 20.0, 30.0, 0.5, {}, 20.0, 20.0,
                raw_scores=scores_b,
            ),
        }
        drivers = {"market_demand": [("Option_A", "VarA"), ("Option_B", "VarB")]}
        driver_samples = {"market_demand": driver_vals}

        voi = calculate_value_of_information(
            mc_results=results,
            is_fully_shared=True,
            drivers=drivers,
            driver_samples=driver_samples,
        )

        assert voi["evpi"]["valid"] is True
        assert pytest.approx(10.0, abs=TOLERANCE) == voi["evpi"]["value"]
        assert pytest.approx(0.40, abs=TOLERANCE) == voi["evpi"]["fraction_of_winner_mean"]

        evppi_list = voi["evppi_by_driver"]
        assert len(evppi_list) == 1
        assert evppi_list[0]["driver"] == "market_demand"
        assert evppi_list[0]["valid"] is True
        assert pytest.approx(10.0, abs=TOLERANCE) == evppi_list[0]["evppi"]
        assert pytest.approx(0.40, abs=TOLERANCE) == evppi_list[0]["evppi_fraction_of_winner_mean"]

    def test_dominant_option_produces_zero_evpi(self) -> None:
        """When one option dominates across every scenario, perfect information has zero value."""
        n_sims = 1000
        # Option A strictly dominates Option B in every simulation draw
        scores_a = np.linspace(80.0, 120.0, n_sims)
        scores_b = np.linspace(20.0, 60.0, n_sims)

        results = {
            "A": Statistics("A", 100.0, 10.0, 80.0, 120.0, 82.0, 118.0, 1.0, {}, 82.0, 80.0, raw_scores=scores_a),
            "B": Statistics("B", 40.0, 10.0, 20.0, 60.0, 22.0, 58.0, 0.0, {}, 22.0, 20.0, raw_scores=scores_b),
        }
        voi = calculate_value_of_information(
            mc_results=results,
            is_fully_shared=True,
            drivers={"factor": [("A", "X"), ("B", "X")]},
            driver_samples={"factor": np.random.uniform(size=n_sims)},
        )

        assert voi["evpi"]["valid"] is True
        assert pytest.approx(0.0, abs=TOLERANCE) == voi["evpi"]["value"]
        assert pytest.approx(0.0, abs=TOLERANCE) == voi["evpi"]["fraction_of_winner_mean"]

    def test_unshared_model_returns_none_evpi_with_explanation(self) -> None:
        """When options are sampled independently, EVPI is None and provides an explicit explanation."""
        scores_a = np.array([10.0, 20.0, 30.0])
        scores_b = np.array([30.0, 20.0, 10.0])
        results = {
            "A": Statistics("A", 20.0, 8.16, 10.0, 30.0, 11.0, 29.0, 0.5, {}, 11.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 20.0, 8.16, 10.0, 30.0, 11.0, 29.0, 0.5, {}, 11.0, 10.0, raw_scores=scores_b),
        }
        voi = calculate_value_of_information(
            mc_results=results,
            is_fully_shared=False,
            drivers={},
        )

        assert voi["evpi"]["value"] is None
        assert voi["evpi"]["fraction_of_winner_mean"] is None
        assert voi["evpi"]["valid"] is False
        assert "las opciones se muestrean de forma independiente: el EVPI mediría ruido de muestreo, no información" in voi["evpi"]["reason"]

    def test_evppi_driver_ranking_orders_descending(self) -> None:
        """Drivers must be ranked in descending order of EVPPI to prioritize investigation."""
        n_sims = 1000
        u_critical = np.concatenate([np.full(500, 0.1), np.full(500, 0.9)])
        u_minor = np.random.uniform(0.0, 1.0, n_sims)

        # Critical driver dictates a large flip between A and B
        scores_a = np.concatenate([np.full(500, 10.0), np.full(500, 50.0)])
        scores_b = np.concatenate([np.full(500, 40.0), np.full(500, 20.0)])

        results = {
            "A": Statistics("A", 30.0, 20.0, 10.0, 50.0, 12.0, 48.0, 0.5, {}, 12.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 30.0, 10.0, 20.0, 40.0, 21.0, 39.0, 0.5, {}, 21.0, 20.0, raw_scores=scores_b),
        }
        drivers = {
            "minor_noise": [("A", "N1"), ("B", "N1")],
            "critical_risk": [("A", "C1"), ("B", "C1")],
        }
        driver_samples = {
            "minor_noise": u_minor,
            "critical_risk": u_critical,
        }

        voi = calculate_value_of_information(
            mc_results=results,
            is_fully_shared=True,
            drivers=drivers,
            driver_samples=driver_samples,
        )

        evppi_list = voi["evppi_by_driver"]
        assert len(evppi_list) == 2
        # The critical risk must rank first
        assert evppi_list[0]["driver"] == "critical_risk"
        assert evppi_list[0]["evppi"] >= evppi_list[1]["evppi"]

    @given(
        s_a0=st.floats(min_value=0.0, max_value=100.0),
        s_a1=st.floats(min_value=0.0, max_value=100.0),
        s_b0=st.floats(min_value=0.0, max_value=100.0),
        s_b1=st.floats(min_value=0.0, max_value=100.0),
    )
    def test_property_evpi_nonnegative_and_evppi_bounded_by_evpi(
        self, s_a0: float, s_a1: float, s_b0: float, s_b1: float,
    ) -> None:
        """Axiomatic property: EVPI >= 0 always, and EVPPI(driver) <= EVPI."""
        scores_a = np.array([s_a0, s_a1])
        scores_b = np.array([s_b0, s_b1])
        results = {
            "A": Statistics("A", float(np.mean(scores_a)), 1.0, 0.0, 100.0, 0.0, 100.0, 0.5, {}, 0.0, 0.0, raw_scores=scores_a),
            "B": Statistics("B", float(np.mean(scores_b)), 1.0, 0.0, 100.0, 0.0, 100.0, 0.5, {}, 0.0, 0.0, raw_scores=scores_b),
        }
        drivers = {"driver1": [("A", "V1"), ("B", "V1")]}
        driver_samples = {"driver1": np.array([0.2, 0.8])}

        voi = calculate_value_of_information(
            mc_results=results,
            is_fully_shared=True,
            drivers=drivers,
            driver_samples=driver_samples,
        )

        evpi = voi["evpi"]["value"]
        assert evpi is not None
        assert evpi >= -1e-9

        for item in voi["evppi_by_driver"]:
            evppi = item["evppi"]
            assert evppi >= -1e-9
            assert evppi <= evpi + 1e-9

    @pytest.mark.asyncio
    async def test_orchestrator_returns_value_of_information_and_maturity(self) -> None:
        """Integration test: UnifiedDecisionFramework includes VoI and maturity in result."""
        from decision_maker.core.orchestrator import UnifiedDecisionFramework

        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 500
        fw.mc_engine.seed = 123
        fw.add_factor(Factor("Profit", weight=1.0, maximize=True))

        opt_a = DecisionOption("A")
        opt_a.add_variable("Profit", DistributionType.NORMAL, 100.0, 2.0, driver="market")
        fw.add_option(opt_a)

        opt_b = DecisionOption("B")
        opt_b.add_variable("Profit", DistributionType.NORMAL, 50.0, 2.0, driver="market")
        fw.add_option(opt_b)

        res = await fw.run_analysis(mode="express", results_dir=None)

        assert "value_of_information" in res
        voi = res["value_of_information"]
        assert "evpi" in voi
        assert voi["evpi"]["valid"] is True
        assert "evppi_by_driver" in voi

        assert "engine_maturity" in res
        maturity = res["engine_maturity"]
        assert "MonteCarlo" in maturity
        assert maturity["MonteCarlo"] == "validated"
        assert maturity["TOPSIS"] == "characterized"
