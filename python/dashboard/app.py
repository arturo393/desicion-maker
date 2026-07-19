"""Streamlit dashboard for the Decision Maker framework."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def run_dashboard():
    """Launch the Streamlit dashboard."""
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "streamlit and plotly required: pip install streamlit plotly"
        )

    st.set_page_config(
        page_title="Decision Maker",
        page_icon="📊",
        layout="wide",
    )
    st.title("📊 Decision Maker Dashboard")
    st.markdown("Multi-Criteria Decision Intelligence Framework")

    tab_new, tab_history, tab_templates, tab_about = st.tabs(
        ["New Analysis", "History", "Templates", "About"]
    )

    with tab_new:
        _render_new_analysis()

    with tab_history:
        _render_history()

    with tab_templates:
        _render_templates()

    with tab_about:
        _render_about()


def _render_new_analysis():
    import streamlit as st

    st.header("Run New Analysis")

    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Analysis Name", "My Decision")
            mode = st.selectbox("Mode", ["express", "standard", "advanced"])
        with col2:
            sims = st.number_input("Simulations", 100, 100000, 10000, step=1000)

        st.subheader("Factors")
        n_factors = st.number_input("Number of factors", 1, 10, 3, key="nf")
        factors = []
        for i in range(int(n_factors)):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                fname = st.text_input(f"Name", f"Factor {i+1}", key=f"fn_{i}")
            with cols[1]:
                fw = st.number_input(f"Weight", 0.0, 1.0, 1.0 / n_factors, key=f"fw_{i}")
            with cols[2]:
                fdir = st.selectbox(f"Direction", ["maximize", "minimize"], key=f"fd_{i}")
            factors.append({"name": fname, "weight": fw, "maximize": fdir == "maximize"})

        st.subheader("Options")
        n_opts = st.number_input("Number of options", 2, 10, 3, key="no")
        options = []
        for i in range(int(n_opts)):
            oname = st.text_input(f"Option name", f"Option {i+1}", key=f"on_{i}")
            options.append({"name": oname, "variables": {}})
            for f in factors:
                col1, col2 = st.columns(2)
                with col1:
                    dist = st.selectbox(
                        f"{f['name']} dist", ["deterministic", "normal", "uniform"],
                        key=f"dist_{i}_{f['name']}",
                    )
                with col2:
                    params = st.text_input(
                        f"{f['name']} params (comma-sep)", "100,10",
                        key=f"par_{i}_{f['name']}",
                    )
                options[-1]["variables"][f["name"]] = {
                    "distribution": dist,
                    "params": [float(x.strip()) for x in params.split(",") if x.strip()],
                }

        submitted = st.form_submit_button("Run Analysis", type="primary")

    if submitted:
        with st.spinner("Running analysis..."):
            _execute_analysis(name, mode, sims, factors, options)
            st.success("Analysis complete!")


def _execute_analysis(
    name: str, mode: str, sims: int,
    factors: List[Dict], options: List[Dict],
):
    import streamlit as st
    import asyncio
    from python.core.models import DecisionOption, DistributionType, Factor
    from python.core.orchestrator import UnifiedDecisionFramework
    from python.core.utils import DISTRIBUTION_MAP

    fw = UnifiedDecisionFramework()
    fw.mc_engine.num_simulations = sims
    for f in factors:
        fw.add_factor(Factor(**f))
    for o in options:
        opt = DecisionOption(o["name"], "")
        for vname, vcfg in o["variables"].items():
            dt = DISTRIBUTION_MAP.get(vcfg["distribution"], DistributionType.DETERMINISTIC)
            opt.add_variable(vname, dt, *vcfg["params"])
        fw.add_option(opt)

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(fw.run_analysis(mode=mode))
    finally:
        loop.close()

    # Save to registry
    from python.core.registry import DecisionRegistry
    registry = DecisionRegistry()
    registry.save_decision(
        name=name, mode=mode, num_simulations=sims,
        factors=factors, options=options,
        results=_simplify_result(result),
    )

    # Display results
    mc = result.get("mc_results", {})
    if mc:
        st.subheader("Results")
        df = pd.DataFrame([
            {"Option": n, "Score": s.mean_score, "Std": s.std_dev,
             "CVaR": s.cvar_95, "Success": f"{s.success_rate:.0%}"}
            for n, s in mc.items()
        ]).sort_values("Score", ascending=False)
        st.dataframe(df, use_container_width=True)

        fig = go.Figure()
        for n, s in mc.items():
            fig.add_trace(go.Box(y=s.raw_scores, name=n))
        fig.update_layout(title="Score Distribution", yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)

    explanation = result.get("explanation", "")
    if explanation:
        with st.expander("Decision Explanation", expanded=True):
            st.markdown(explanation)

    antifragile = result.get("antifragile", {})
    if antifragile:
        with st.expander("Antifragile Analysis"):
            st.json(antifragile)


def _simplify_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Remove large arrays for JSON storage."""
    from copy import deepcopy
    simple = deepcopy(result)
    mc = simple.get("mc_results", {})
    if mc:
        for n, s in mc.items():
            s.raw_scores = None
            s.raw_factor_data = None
    return simple


def _render_history():
    import streamlit as st
    import pandas as pd

    st.header("Decision History")
    try:
        from python.core.registry import DecisionRegistry
        registry = DecisionRegistry()
        items = registry.list_decisions(limit=50)
        if items:
            df = pd.DataFrame(items)
            if "tags" in df.columns:
                df["tags"] = df["tags"].apply(
                    lambda x: ", ".join(json.loads(x)) if isinstance(x, str) else ""
                )
            st.dataframe(df[["id", "name", "mode", "created_at", "status"]],
                         use_container_width=True)

            selected = st.selectbox("View decision", [i["id"] for i in items],
                                    format_func=lambda x: f"#{x} - {next(i['name'] for i in items if i['id']==x)}")
            if selected:
                dec = registry.get_decision(selected)
                if dec:
                    st.json(dec.get("results_json", {}), expanded=False)
        else:
            st.info("No decisions in registry yet.")
    except Exception as e:
        st.error(f"Could not load history: {e}")


def _render_templates():
    import streamlit as st
    import pandas as pd

    st.header("Decision Templates")
    try:
        from python.core.registry import DecisionRegistry
        registry = DecisionRegistry()
        registry.seed_default_templates()
        items = registry.list_templates()
        if items:
            df = pd.DataFrame(items)
            st.dataframe(df[["name", "description", "category"]], use_container_width=True)
        else:
            st.info("No templates available.")
    except Exception as e:
        st.error(f"Could not load templates: {e}")


def _render_about():
    import streamlit as st

    st.header("About")
    st.markdown("""
    **Decision Maker Framework** v3.0

    Multi-Criteria Decision Intelligence Framework with:
    - Monte Carlo simulation
    - TOPSIS / PROMETHEE / AHP
    - Explainability & Counterfactual analysis
    - What-If interactive mode
    - Antifragile strategy detection
    - Group decision consensus
    - Portfolio optimization
    - Topological data analysis
    """)


if __name__ == "__main__":
    run_dashboard()
