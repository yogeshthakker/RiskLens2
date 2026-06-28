import os
import sys
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from groq import Groq
from agent.tools import run_tool
from agent.prompts import SYSTEM_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── fix float32 / numpy types not being JSON serializable ──
class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer)):
            return int(obj)
        if isinstance(obj, (np.floating)):
            return float(obj)
        if isinstance(obj, (np.ndarray)):
            return obj.tolist()
        if isinstance(obj, (np.bool_)):
            return bool(obj)
        return super().default(obj)

def gather_data(account_id: str) -> dict:
    print(f"  collecting profile...")
    profile = run_tool("get_account_profile", {"account_id": account_id})

    print(f"  collecting transactions...")
    transactions = run_tool("get_transaction_summary", {"account_id": account_id})

    print(f"  collecting connections...")
    connections = run_tool("get_connections", {"account_id": account_id})
    # if neo4j fails, use a safe fallback
    if "error" in connections:
        print(f"  graph unavailable: {connections['error']}")
        connections = {
            "account_id"  : account_id,
            "total_found" : 0,
            "connections" : [],
            "note"        : "graph unavailable during this run"
        }

    print(f"  collecting risk score...")
    risk = run_tool("get_risk_score", {"account_id": account_id})
    if "error" in risk:
        print(f"  risk engine error: {risk['error']}")
        risk = {
            "account_id" : account_id,
            "risk_score" : 0,
            "risk_level" : "Unknown",
            "top_reasons": [],
        }

    return {
        "account_id"  : account_id,
        "profile"     : profile,
        "transactions": transactions,
        "connections" : connections,
        "risk"        : risk
    }

def investigate(account_id: str) -> str:
    print(f"\ninvestigating {account_id}...")

    data = gather_data(account_id)

    # safely serialize — handles float32 and numpy types
    data_str = json.dumps(data, indent=2, cls=SafeEncoder)

    user_prompt = f"""
You are a banking compliance analyst. Based on the following data,
write a structured investigation report.

ACCOUNT DATA:
{data_str}

Write the report in exactly this format:

---
INVESTIGATION REPORT
─────────────────────────────────────────
Entity       : [owner name and type]
Account      : [account ID]
Risk Score   : [score]/100 — [Low/Medium/High]

OBSERVATIONS
- [observation based on transaction behaviour]
- [observation based on connections found]
- [observation based on risk score reasons]
- [any additional relevant findings]

CONNECTED ENTITIES
- [list key connections found]

RECOMMENDATION
[One clear paragraph on what the analyst should do next]
─────────────────────────────────────────

Be factual. Only use what is in the data above. Do not invent anything.
"""

    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        max_tokens = 1500
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    import pandas as pd

    df         = pd.read_csv("data/processed/features.csv")
    suspicious = df[df["label"] == 1]["account_id"].values

    if len(suspicious) == 0:
        print("no suspicious accounts to investigate")
    else:
        test_id = suspicious[0]
        report  = investigate(test_id)
        print("\n" + report)