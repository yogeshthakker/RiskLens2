import pandas as pd
import numpy as np
import pickle
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv("data/processed/features.csv")

FEATURES = [
    "total_txns", "total_amount", "avg_amount",
    "spike_ratio", "intl_ratio", "unique_receivers",
    "suspicious_ratio", "cash_ratio", "has_alert",
    "is_frozen", "is_dormant", "kyc_flagged", "kyc_pending"
]

X = df[FEATURES]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

os.makedirs("warning_engine/models", exist_ok=True)
with open("warning_engine/models/xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("model saved to warning_engine/models/xgb_model.pkl")