from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.graph_routes  import router as graph_router
from routes.risk_routes   import router as risk_router
from routes.report_routes import router as report_router

app = FastAPI(title="RiskLens API", version="1.0.0")

# allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(graph_router,  prefix="/api")
app.include_router(risk_router,   prefix="/api")
app.include_router(report_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "RiskLens API is running"}

@app.get("/api/accounts")
def get_accounts():
    import pandas as pd
    df = pd.read_csv("data/processed/features.csv")
    suspicious = df[df["label"] == 1]["account_id"].tolist()
    all_accounts = df["account_id"].tolist()
    return {
        "total"      : len(all_accounts),
        "suspicious" : len(suspicious),
        "accounts"   : all_accounts,
        "flagged"    : suspicious
    }