import pandas as pd
import shap
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warning_engine.predict import model, df, FEATURES

def explain_risk(account_id: str) -> dict:
    row = df[df["account_id"] == account_id]

    if row.empty:
        return {"error": "account not found"}

    X = row[FEATURES]

    explainer   = shap.TreeExplainer(model)
    shap_vals   = explainer.shap_values(X)
    shap_series = pd.Series(shap_vals[0], index=FEATURES)

    top_positive = shap_series[shap_series > 0]\
                   .sort_values(ascending=False).head(3)

    top_negative = shap_series[shap_series < 0]\
                   .sort_values().head(2)

    risk_factors = []
    for feature in top_positive.index:
        value = round(row[feature].values[0], 2)
        risk_factors.append({
            "feature"   : feature,
            "direction" : "increases risk",
            "value"     : value,
            "impact"    : round(shap_series[feature], 4)
        })

    protective_factors = []
    for feature in top_negative.index:
        value = round(row[feature].values[0], 2)
        protective_factors.append({
            "feature"   : feature,
            "direction" : "reduces risk",
            "value"     : value,
            "impact"    : round(shap_series[feature], 4)
        })

    return {
        "account_id"         : account_id,
        "risk_factors"       : risk_factors,
        "protective_factors" : protective_factors
    }

if __name__ == "__main__":
    suspicious = df[df["label"] == 1]["account_id"].values

    if len(suspicious) == 0:
        print("no suspicious accounts found")
    else:
        test_id = suspicious[0]
        result  = explain_risk(test_id)

        print(f"\nExplanation for {result['account_id']}")

        print("\nWhat is pushing risk UP:")
        for r in result["risk_factors"]:
            print(f"  • {r['feature']} = {r['value']} → impact {r['impact']}")

        print("\nWhat is pushing risk DOWN:")
        for r in result["protective_factors"]:
            print(f"  • {r['feature']} = {r['value']} → impact {r['impact']}")