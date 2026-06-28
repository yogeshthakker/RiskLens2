from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.agent import investigate

router = APIRouter()

@router.post("/report/{account_id}")
def generate_report(account_id: str):
    try:
        report = investigate(account_id)
        return {"account_id": account_id, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))