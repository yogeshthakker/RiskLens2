from fastapi import APIRouter, HTTPException
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.tools import tool_get_risk_score

router = APIRouter()

def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean(i) for i in obj]
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj

@router.get("/risk/{account_id}")
def get_risk(account_id: str):
    result = tool_get_risk_score(account_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return clean(result)