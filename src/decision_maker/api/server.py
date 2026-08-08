
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

from decision_maker.api.templates import TEMPLATES
from decision_maker.core.db import get_session
from decision_maker.core.db_models import AnalysisSession, OutcomeRecord
from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework

app = FastAPI(title="Decision Maker God-Mode API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FactorSchema(BaseModel):
    name: str
    weight: float
    maximize: bool = True
    category: str = "General"
    stakeholder_weights: dict[str, float] | None = None

class VariableSchema(BaseModel):
    distribution: str
    params: list[float]

class OptionSchema(BaseModel):
    name: str
    description: str = ""
    variables: dict[str, VariableSchema]

class AnalysisRequest(BaseModel):
    name: str = "New Analysis"
    description: str = ""
    factors: list[FactorSchema]
    options: list[OptionSchema]
    mode: str = "advanced"
    use_ai: bool = False

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    try:
        from decision_maker.core.utils import DISTRIBUTION_MAP
        fw = UnifiedDecisionFramework()
        fw.mc_engine.num_simulations = 10000
        for f in req.factors:
            kwargs = {"name": f.name, "weight": f.weight, "maximize": f.maximize, "category": f.category}
            if f.stakeholder_weights is not None:
                kwargs["stakeholder_weights"] = f.stakeholder_weights
            fw.add_factor(Factor(**kwargs))
        for o in req.options:
            opt = DecisionOption(name=o.name, description=o.description)
            for vname, vcfg in o.variables.items():
                dt = DISTRIBUTION_MAP.get(vcfg.distribution, DistributionType.DETERMINISTIC)
                opt.add_variable(vname, dt, *vcfg.params)
            fw.add_option(opt)

        result = await fw.run_analysis(mode=req.mode, use_ai=req.use_ai)
        session_id = fw.save_session(req.name, req.description)

        # Format the output for the UI
        topsis = result.get("topsis_scores", {})
        if hasattr(topsis, "to_dict"):
            topsis = topsis.to_dict()

        future = result.get("future", {})
        serialized_future = {}
        for k, v in future.items():
            if hasattr(v, "to_dict"):
                serialized_future[k] = v.to_dict()
            else:
                serialized_future[k] = v

        mc_res = {}
        for opt_name, stats in result.get("mc_results", {}).items():
            mc_res[opt_name] = {
                "mean_score": float(stats.mean_score),
                "std_dev": float(stats.std_dev),
                "success_rate": float(stats.success_rate),
                "percentile_5": float(stats.percentile_5),
                "percentile_95": float(stats.percentile_95)
            }

        winner = None
        if topsis:
            winner = list(topsis.keys())[0]

        return {
            "session_id": session_id,
            "status": "completed",
            "mc_results": mc_res,
            "topsis_scores": topsis,
            "future_metrics": serialized_future,
            "explanation": result.get("explanation", ""),
            "winner": winner
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
def list_sessions():
    session = next(get_session())
    statements = select(AnalysisSession)
    results = session.exec(statements).all()
    return [{"id": s.id, "name": s.name, "description": s.description} for s in results]

@app.get("/sessions/{session_id}")
def get_session_data(session_id: str):
    session = next(get_session())
    db_session = session.get(AnalysisSession, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": db_session.id,
        "name": db_session.name,
        "factors": db_session.factors_json,
        "options": db_session.options_json
    }

class OutcomeRequest(BaseModel):
    actual_winner: str
    actual_score: float
    notes: str | None = None

@app.get("/templates")
def list_templates():
    return TEMPLATES

@app.post("/sessions/{session_id}/outcome")
def register_outcome(session_id: str, req: OutcomeRequest):
    session = next(get_session())
    db_session = session.get(AnalysisSession, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Super simple accuracy calculation (just for demonstration)
    accuracy = 100.0 if req.actual_winner else 0.0 # Logic can be expanded

    outcome = OutcomeRecord(
        session_id=session_id,
        actual_winner=req.actual_winner,
        actual_score=req.actual_score,
        accuracy_percentage=accuracy,
        notes=req.notes
    )
    session.add(outcome)
    session.commit()
    session.refresh(outcome)
    return outcome

def run_server(host="0.0.0.0", port=8001):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
