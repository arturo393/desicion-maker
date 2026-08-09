"""
JSON schema validating the structure of saved analysis reports.
Usage: from decision_maker.core.report_schema import REPORT_SCHEMA, validate_report
Does NOT: Serialize reports (see reporting.save_json_report) or run decision algorithms.
"""

from __future__ import annotations

__all__ = ["REPORT_SCHEMA", "validate_report"]

import jsonschema

REPORT_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "decision_matrix", "monte_carlo", "topsis", "algorithm_comparison", "ai_insights"],
    "properties": {
        "timestamp": {"type": "string"},
        "decision_matrix": {"type": "object"},
        "monte_carlo": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["mean", "std", "min", "max", "p5", "p95", "var_95", "cvar_95", "success_rate"],
                "properties": {
                    "mean": {"type": "number"},
                    "std": {"type": "number"},
                    "min": {"type": "number"},
                    "max": {"type": "number"},
                    "p5": {"type": "number"},
                    "p95": {"type": "number"},
                    "var_95": {"type": "number"},
                    "cvar_95": {"type": "number"},
                    "success_rate": {"type": "number"},
                },
            },
        },
        "topsis": {"type": "object"},
        "algorithm_comparison": {"type": "object"},
        "ai_insights": {"type": "object"},
    },
}


def validate_report(data: dict) -> None:
    """Validate an analysis report dict against REPORT_SCHEMA. Raises ValidationError on mismatch."""
    jsonschema.validate(instance=data, schema=REPORT_SCHEMA)
