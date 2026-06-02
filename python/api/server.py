"""FastAPI server for the Decision Maker framework."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    raise ImportError("fastapi and uvicorn required: pip install fastapi uvicorn")


# ── Pydantic schemas (module level so FastAPI can resolve type hints) ──

class _FactorSchema(BaseModel):
    name: str
    weight: float
    maximize: bool = True
    category: str = "General"


class _VariableSchema(BaseModel):
    distribution: str
    params: List[float]


class _OptionSchema(BaseModel):
    name: str
    description: str = ""
    variables: Dict[str, _VariableSchema]


class _AnalysisRequest(BaseModel):
    factors: list[_FactorSchema]
    options: list[_OptionSchema]
    mode: str = "standard"
    simulations: int = 10000
    name: str = ""
    description: str = ""


class _AnalysisResponse(BaseModel):
    id: int
    status: str
    summary: Dict[str, Any]


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Decision Maker API",
        description="Multi-Criteria Decision Intelligence Framework",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── In-memory registry (lazy import to avoid startup cost) ──

    def _get_registry():
        from python.core.registry import DecisionRegistry
        reg = DecisionRegistry()
        reg.seed_default_templates()
        return reg

    def _run_analysis(req: _AnalysisRequest) -> Dict[str, Any]:
        from python.core.models import DecisionOption, DistributionType, Factor
        from python.core.orchestrator import UnifiedDecisionFramework
        import asyncio

        DIST_MAP = {
            "deterministic": DistributionType.DETERMINISTIC,
            "normal": DistributionType.NORMAL,
            "uniform": DistributionType.UNIFORM,
            "triangular": DistributionType.TRIANGULAR,
            "bernoulli": DistributionType.BERNOULLI,
            "exponential": DistributionType.EXPONENTIAL,
            "beta": DistributionType.BETA,
            "lognormal": DistributionType.LOGNORMAL,
            "gamma": DistributionType.GAMMA,
            "poisson": DistributionType.POISSON,
        }

        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = req.simulations

        for f in req.factors:
            fw.add_factor(Factor(f.name, f.weight, f.maximize, f.category))

        for o in req.options:
            opt = DecisionOption(o.name, o.description)
            for vname, vcfg in o.variables.items():
                dt = DIST_MAP.get(vcfg.distribution, DistributionType.DETERMINISTIC)
                opt.add_variable(vname, dt, *vcfg.params)
            fw.add_option(opt)

        result = asyncio.run(fw.run_analysis(mode=req.mode))
        return result

    # ── Routes ──

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/analyze", response_model=_AnalysisResponse)
    def analyze(req: _AnalysisRequest):
        try:
            result = _run_analysis(req)
            registry = _get_registry()
            factors_dict = [f.model_dump() for f in req.factors]
            options_dict = [o.model_dump() for o in req.options]
            rid = registry.save_decision(
                name=req.name or f"API Analysis",
                mode=req.mode,
                num_simulations=req.simulations,
                factors=factors_dict,
                options=options_dict,
                results=result,
                description=req.description,
            )
            return _AnalysisResponse(
                id=rid,
                status="completed",
                summary={
                    "winner": result.get("explanation", ""),
                    "mode": req.mode,
                    "option_count": len(req.options),
                    "factor_count": len(req.factors),
                },
            )
        except Exception as e:
            logger.exception("Analysis failed")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/decisions")
    def list_decisions(limit: int = 20, search: Optional[str] = None):
        registry = _get_registry()
        return registry.list_decisions(limit=limit, search=search)

    @app.get("/decisions/{decision_id}")
    def get_decision(decision_id: int):
        registry = _get_registry()
        result = registry.get_decision(decision_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Decision not found")
        return result

    @app.delete("/decisions/{decision_id}")
    def delete_decision(decision_id: int):
        registry = _get_registry()
        if not registry.delete_decision(decision_id):
            raise HTTPException(status_code=404, detail="Decision not found")
        return {"status": "deleted"}

    @app.get("/templates")
    def list_templates(category: Optional[str] = None):
        registry = _get_registry()
        return registry.list_templates(category=category)

    @app.post("/templates/{name}/apply")
    def apply_template(name: str):
        registry = _get_registry()
        tpl = registry.get_template_by_name(name)
        if tpl is None:
            raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
        return {
            "name": tpl["name"],
            "description": tpl["description"],
            "factors": tpl.get("factors_json"),
            "options": tpl.get("options_json"),
        }

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server."""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn required: pip install uvicorn")
    app = create_app()
    logger.info(f"Starting Decision Maker API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
