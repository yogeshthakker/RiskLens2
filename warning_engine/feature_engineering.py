import pandas as pd
import numpy as np
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build_features():
    transactions = pd.read_csv("data/raw/transactions.csv")
    accounts     = pd.read_csv("data/raw/accounts.csv")
    customers    = pd.read_csv("data/raw/customers.csv")
    alerts       = pd.read_csv("data/raw/alerts.csv")

    transactions["date"] = pd.to_datetime(transactions["date"])

    features = []

    for account_id in accounts["account_id"].unique():
        txns = transactions[transactions["sender_account"] == account_id]

        # ── basic volume ──────────────────────────────────────
        total_txns   = len(txns)
        total_amount = txns["amount"].sum()
        avg_amount   = txns["amount"].mean() if total_txns > 0 else 0

        # ── BEHAVIOURAL signals (this is what fixes the lagging indicator problem)

        # 1. Transaction spike — did volume suddenly jump?
        if total_txns > 0:
            txns_sorted  = txns.sort_values("date")
            recent       = txns_sorted.tail(5)["amount"].mean()
            older        = txns_sorted.head(5)["amount"].mean() if len(txns_sorted) >= 5 else recent
            spike_ratio  = recent / older if older > 0 else 1.0
        else:
            spike_ratio  = 1.0

        # 2. International exposure — how much money went international?
        swift_txns       = txns[txns["type"] == "SWIFT"]
        intl_ratio       = len(swift_txns) / total_txns if total_txns > 0 else 0

        # 3. Unique counterparties — suddenly talking to many new accounts?
        unique_receivers = txns["receiver_account"].nunique()

        # 4. Suspicious transaction ratio
        suspicious_count = txns["is_suspicious"].sum()
        suspicious_ratio = suspicious_count / total_txns if total_txns > 0 else 0

        # 5. Cash transaction ratio — high cash = higher risk
        cash_txns  = txns[txns["type"].isin(["Cash Deposit", "Cash Withdrawal"])]
        cash_ratio = len(cash_txns) / total_txns if total_txns > 0 else 0

        # 6. Has active alert?
        has_alert = 1 if account_id in alerts["account_flagged"].values else 0

        # ── account info ──────────────────────────────────────
        acc = accounts[accounts["account_id"] == account_id].iloc[0]
        is_frozen  = 1 if acc["status"] == "Frozen"  else 0
        is_dormant = 1 if acc["status"] == "Dormant" else 0

        # ── KYC status of owner ───────────────────────────────
        owner_id  = acc["owner_id"]
        cust_match = customers[customers["customer_id"] == owner_id]
        if not cust_match.empty:
            kyc = cust_match.iloc[0]["kyc_status"]
            kyc_flagged  = 1 if kyc == "Flagged"  else 0
            kyc_pending  = 1 if kyc == "Pending"  else 0
        else:
            kyc_flagged = 0
            kyc_pending = 0

        # ── label — this is what the model learns from ────────
        # suspicious if: has alert OR suspicious transactions OR frozen
        label = 1 if (has_alert or suspicious_count > 0 or is_frozen) else 0

        features.append({
            "account_id"       : account_id,
            "total_txns"       : total_txns,
            "total_amount"     : total_amount,
            "avg_amount"       : avg_amount,
            "spike_ratio"      : spike_ratio,
            "intl_ratio"       : intl_ratio,
            "unique_receivers" : unique_receivers,
            "suspicious_ratio" : suspicious_ratio,
            "cash_ratio"       : cash_ratio,
            "has_alert"        : has_alert,
            "is_frozen"        : is_frozen,
            "is_dormant"       : is_dormant,
            "kyc_flagged"      : kyc_flagged,
            "kyc_pending"      : kyc_pending,
            "label"            : label
        })

    df = pd.DataFrame(features).fillna(0)
    df.to_csv("data/processed/features.csv", index=False)
    print(f"features built for {len(df)} accounts")
    print(f"suspicious accounts found: {df['label'].sum()}")
    return df

if __name__ == "__main__":
    build_features()