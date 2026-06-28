import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

# ── 1. CUSTOMERS ──────────────────────────────────────────
def generate_customers(n=500):
    customers = []
    for i in range(n):
        customers.append({
            "customer_id": f"CUST{1000+i}",
            "name": fake.name(),
            "age": random.randint(25, 65),
            "address": fake.address().replace("\n", ", "),
            "occupation": random.choice([
                "Business Owner", "Trader", "Engineer",
                "Doctor", "Consultant", "Retired"
            ]),
            "account_opened": fake.date_between(
                start_date="-10y", end_date="-1y"
            ),
            "kyc_status": random.choice(
                ["Verified", "Verified", "Verified", "Pending", "Flagged"]
            ),
            "risk_label": "normal"  # we will flip some to suspicious later
        })
    return pd.DataFrame(customers)

# ── 2. COMPANIES ──────────────────────────────────────────
def generate_companies(customers_df, n=100):
    companies = []
    for i in range(n):
        owner = customers_df.sample(1).iloc[0]
        companies.append({
            "company_id": f"COMP{2000+i}",
            "company_name": fake.company(),
            "registration_number": fake.bothify(text="REG-#####"),
            "industry": random.choice([
                "Import/Export", "Real Estate", "Consulting",
                "Manufacturing", "IT Services", "Trading"
            ]),
            "director_customer_id": owner["customer_id"],
            "director_name": owner["name"],
            "incorporated_date": fake.date_between(
                start_date="-8y", end_date="-1y"
            ),
            "country": random.choice([
                "India", "UAE", "Germany", "Singapore",
                "Cayman Islands", "British Virgin Islands"  # suspicious jurisdictions
            ])
        })
    return pd.DataFrame(companies)

# ── 3. ACCOUNTS ───────────────────────────────────────────
def generate_accounts(customers_df, companies_df, n=800):
    accounts = []
    for i in range(n):
        # mix of customer-owned and company-owned accounts
        if random.random() > 0.4:
            owner = customers_df.sample(1).iloc[0]
            owner_id = owner["customer_id"]
            owner_type = "customer"
        else:
            owner = companies_df.sample(1).iloc[0]
            owner_id = owner["company_id"]
            owner_type = "company"

        accounts.append({
            "account_id": f"ACC{3000+i}",
            "owner_id": owner_id,
            "owner_type": owner_type,
            "account_type": random.choice(
                ["Savings", "Current", "Business", "NRE"]
            ),
            "opening_date": fake.date_between(
                start_date="-7y", end_date="-6m"
            ),
            "balance": round(random.uniform(1000, 500000), 2),
            "currency": random.choice(["INR", "USD", "EUR", "AED"]),
            "status": random.choice(
                ["Active", "Active", "Active", "Dormant", "Frozen"]
            )
        })
    return pd.DataFrame(accounts)

# ── 4. TRANSACTIONS ───────────────────────────────────────
def generate_transactions(accounts_df, n=50000):
    transactions = []
    account_ids = accounts_df["account_id"].tolist()

    for i in range(n):
        sender = random.choice(account_ids)
        receiver = random.choice([a for a in account_ids if a != sender])
        amount = round(random.uniform(500, 50000), 2)
        date = fake.date_between(start_date="-1y", end_date="today")

        transactions.append({
            "txn_id": f"TXN{4000+i}",
            "sender_account": sender,
            "receiver_account": receiver,
            "amount": amount,
            "currency": random.choice(["INR", "USD", "EUR"]),
            "date": date,
            "type": random.choice([
                "NEFT", "RTGS", "SWIFT", "Cash Deposit",
                "Cash Withdrawal", "Internal Transfer"
            ]),
            "description": fake.sentence(nb_words=5),
            "is_suspicious": False  # we will flip some below
        })
    return pd.DataFrame(transactions)

# ── 5. PLANT SUSPICIOUS PATTERNS ─────────────────────────
def plant_suspicious_patterns(customers_df, transactions_df, accounts_df):

    # Pattern A — sudden spike: one account sends huge amounts in short burst
    suspicious_account = accounts_df.sample(1).iloc[0]["account_id"]
    for i in range(10):
        date = datetime(2024, 11, 1) + timedelta(days=i)
        transactions_df = pd.concat([transactions_df, pd.DataFrame([{
            "txn_id": f"TXN_SPIKE_{i}",
            "sender_account": suspicious_account,
            "receiver_account": accounts_df.sample(1).iloc[0]["account_id"],
            "amount": round(random.uniform(80000, 200000), 2),
            "currency": "USD",
            "date": date.date(),
            "type": "SWIFT",
            "description": "Urgent transfer",
            "is_suspicious": True
        }])], ignore_index=True)

    # Pattern B — circular flow: A sends to B, B sends to C, C sends back to A
    acc_list = accounts_df.sample(3)["account_id"].tolist()
    for j, (sender, receiver) in enumerate(zip(acc_list, acc_list[1:] + [acc_list[0]])):
        transactions_df = pd.concat([transactions_df, pd.DataFrame([{
            "txn_id": f"TXN_CIRCLE_{j}",
            "sender_account": sender,
            "receiver_account": receiver,
            "amount": 95000.00,
            "currency": "INR",
            "date": datetime(2024, 10, 15).date(),
            "type": "RTGS",
            "description": "Business payment",
            "is_suspicious": True
        }])], ignore_index=True)

    # Mark customers linked to suspicious accounts as suspicious
    suspicious_owners = accounts_df[
        accounts_df["account_id"] == suspicious_account
    ]["owner_id"].values
    customers_df.loc[
        customers_df["customer_id"].isin(suspicious_owners), "risk_label"
    ] = "suspicious"

    return customers_df, transactions_df

# ── 6. ALERTS ─────────────────────────────────────────────
def generate_alerts(transactions_df):
    suspicious_txns = transactions_df[transactions_df["is_suspicious"] == True]
    alerts = []
    for _, txn in suspicious_txns.iterrows():
        alerts.append({
            "alert_id": f"ALT_{txn['txn_id']}",
            "triggered_on": txn["txn_id"],
            "account_flagged": txn["sender_account"],
            "reason": random.choice([
                "Transaction volume spike",
                "Unusual international transfer",
                "Circular money flow detected",
                "High value cash transaction"
            ]),
            "alert_date": txn["date"],
            "status": random.choice(["Open", "Under Review", "Closed"])
        })
    return pd.DataFrame(alerts)

# ── RUN EVERYTHING ────────────────────────────────────────
if __name__ == "__main__":
    customers = generate_customers(500)
    companies = generate_companies(customers, 100)
    accounts  = generate_accounts(customers, companies, 800)
    transactions = generate_transactions(accounts, 50000)
    customers, transactions = plant_suspicious_patterns(
        customers, transactions, accounts
    )
    alerts = generate_alerts(transactions)

    # save to CSV
    customers.to_csv("customers.csv", index=False)
    companies.to_csv("companies.csv", index=False)
    accounts.to_csv("accounts.csv", index=False)
    transactions.to_csv("transactions.csv", index=False)
    alerts.to_csv("alerts.csv", index=False)

    print(f"customers     : {len(customers)}")
    print(f"companies     : {len(companies)}")
    print(f"accounts      : {len(accounts)}")
    print(f"transactions  : {len(transactions)}")
    print(f"alerts        : {len(alerts)}")
    print("All CSVs saved.")