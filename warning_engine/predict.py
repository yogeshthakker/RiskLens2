import pandas as pd
import pickle
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FEATURES = [
    "total_txns", "total_amount", "avg_amount",
    "spike_ratio", "intl_ratio", "unique_receivers",
    "suspicious_ratio", "cash_ratio", "has_alert",
    "is_frozen", "is_dormant", "kyc_flagged", "kyc_pending"
]

with open("warning_engine/models/xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

df = pd.read_csv("data/processed/features.csv")

def predict_risk(account_id: str) -> dict:
    row = df[df["account_id"] == account_id]

    if row.empty:
        return {"error": "account not found"}

    X          = row[FEATURES]
    score      = model.predict_proba(X)[0][1]
    risk_score = round(score * 100, 1)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "account_id" : account_id,
        "risk_score" : risk_score,
        "risk_level" : risk_level
    }

if __name__ == "__main__":
    suspicious = df[df["label"] == 1]["account_id"].values

    if len(suspicious) == 0:
        print("no suspicious accounts found")
    else:
        for test_id in suspicious[:3]:
            result = predict_risk(test_id)
            print(f"\nAccount  : {result['account_id']}")
            print(f"Risk     : {result['risk_level']} ({result['risk_score']}/100)")
            print("-" * 40)