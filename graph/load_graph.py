from neo4j import GraphDatabase
import pandas as pd
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AUTH = ("neo4j", "riskLens123")

URIS = [
    "bolt://localhost:7687",
    "bolt://127.0.0.1:7687",
    "neo4j://localhost:7687",
    "neo4j://127.0.0.1:7687",
]

# auto-find whichever URI works
driver = None
for uri in URIS:
    try:
        d = GraphDatabase.driver(uri, auth=AUTH)
        d.verify_connectivity()
        driver = d
        print(f"connected via {uri}")
        break
    except Exception:
        print(f"skipping {uri}")

if driver is None:
    print("could not connect to Neo4j — make sure it is running in Desktop")
    exit()

customers    = pd.read_csv("data/raw/customers.csv")
companies    = pd.read_csv("data/raw/companies.csv")
accounts     = pd.read_csv("data/raw/accounts.csv")
transactions = pd.read_csv("data/raw/transactions.csv")
alerts       = pd.read_csv("data/raw/alerts.csv")

with driver.session() as s:

    s.run("""
        UNWIND $rows AS row
        MERGE (c:Customer {customer_id: row.customer_id})
        SET c.name       = row.name,
            c.age        = toInteger(row.age),
            c.occupation = row.occupation,
            c.kyc_status = row.kyc_status,
            c.risk_label = row.risk_label
    """, rows=customers.to_dict("records"))
    print("customers loaded")

    s.run("""
        UNWIND $rows AS row
        MERGE (co:Company {company_id: row.company_id})
        SET co.name     = row.company_name,
            co.industry = row.industry,
            co.country  = row.country
    """, rows=companies.to_dict("records"))
    print("companies loaded")

    s.run("""
        UNWIND $rows AS row
        MERGE (a:Account {account_id: row.account_id})
        SET a.type     = row.account_type,
            a.balance  = toFloat(row.balance),
            a.currency = row.currency,
            a.status   = row.status
    """, rows=accounts.to_dict("records"))
    print("accounts loaded")

    s.run("""
        UNWIND $rows AS row
        MATCH (cu:Customer {customer_id: row.director_customer_id})
        MATCH (co:Company  {company_id:  row.company_id})
        MERGE (cu)-[:OWNS]->(co)
    """, rows=companies.to_dict("records"))
    print("owns relationships loaded")

    s.run("""
        UNWIND $rows AS row
        MATCH (a:Account {account_id: row.account_id})
        OPTIONAL MATCH (cu:Customer {customer_id: row.owner_id})
        OPTIONAL MATCH (co:Company  {company_id:  row.owner_id})
        FOREACH (_ IN CASE WHEN cu IS NOT NULL THEN [1] ELSE [] END |
            MERGE (cu)-[:LINKED_TO]->(a))
        FOREACH (_ IN CASE WHEN co IS NOT NULL THEN [1] ELSE [] END |
            MERGE (co)-[:LINKED_TO]->(a))
    """, rows=accounts.to_dict("records"))
    print("linked_to relationships loaded")

    s.run("""
        UNWIND $rows AS row
        MATCH (sender:Account   {account_id: row.sender_account})
        MATCH (receiver:Account {account_id: row.receiver_account})
        MERGE (sender)-[t:TRANSFERS_TO]->(receiver)
        SET t.amount        = toFloat(row.amount),
            t.currency      = row.currency,
            t.date          = row.date,
            t.is_suspicious = toBoolean(row.is_suspicious)
    """, rows=transactions.to_dict("records"))
    print("transfers loaded")

    s.run("""
        UNWIND $rows AS row
        MERGE (al:Alert {alert_id: row.alert_id})
        SET al.reason = row.reason,
            al.status = row.status,
            al.date   = row.alert_date
        WITH al, row
        MATCH (a:Account {account_id: row.account_flagged})
        MERGE (a)-[:HAS_ALERT]->(al)
    """, rows=alerts.to_dict("records"))
    print("alerts loaded")

print("graph fully loaded")
driver.close()