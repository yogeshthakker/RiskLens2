from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.tools import tool_get_connections

router = APIRouter()

@router.get("/graph/{account_id}")
def get_graph(account_id: str):
    result = tool_get_connections(account_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result