import pytest

from decision_maker.core.causal_dag import CausalDAG, CausalNode, CausalEdge
from decision_maker.core.models import Factor


class TestCausalDAG:
    def test_build_with_factors(self):
        factors = [Factor("Cost", 0.4, maximize=False), Factor("Performance", 0.6, maximize=True)]
        dag = CausalDAG.build(factors, ["OptionA", "OptionB"])
        assert dag["num_nodes"] >= 4
        assert dag["num_edges"] >= 3

    def test_empty_factors(self):
        dag = CausalDAG.build([], ["OptionA"])
        assert dag["num_nodes"] >= 2
        assert "decision" in [n["name"] for n in dag["nodes"]]
        assert "outcome" in [n["name"] for n in dag["nodes"]]

    def test_confounder_detection(self):
        factors = [Factor("Risk", 0.5, maximize=False)]
        dag = CausalDAG.build(factors, ["A"])
        confounders = dag["confounders"]
        assert "Risk" in confounders

    def test_thinking_questions(self):
        factors = [Factor("F1", 0.4, maximize=True), Factor("F2", 0.6, maximize=True)]
        dag = CausalDAG.build(factors, ["A", "B"])
        assert len(dag["thinking_questions"]) >= 3

    def test_do_calculus_reminder(self):
        dag = CausalDAG.build([], ["A"])
        assert "do(decision)" in dag["do_calculus_reminder"]

    def test_edges_include_options(self):
        factors = [Factor("F1", 1.0, maximize=True)]
        dag = CausalDAG.build(factors, ["Opt1", "Opt2"])
        decision_edges = [e for e in dag["edges"] if e["source"] == "decision"]
        assert len(decision_edges) == 2

    def test_warnings_for_confounders(self):
        factors = [Factor("HighWeight", 0.8, maximize=False)]
        dag = CausalDAG.build(factors, ["A"])
        assert len(dag["warnings"]) > 0
