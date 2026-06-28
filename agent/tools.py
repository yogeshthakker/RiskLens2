import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from warning_engine.predict import predict_risk
from warning_engine.explain import explain_risk
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

URIS = [
    "bolt://localhost:7687",
    "bolt://127.0.0.1:7687",
    "neo4j://localhost:7687",
    "neo4j://127.0.0.1:7687",
]
AUTH = ("neo4j", "riskLens123")

def get_driver():
    for uri in URIS:
        try:
            d = GraphDatabase.driver(uri, auth=AUTH)
            d.verify_connectivity()
            return d
        except Exception as e:
            continue
    print("  warning: could not connect to Neo4j — check it is running in Desktop")
    return None

def tool_get_account_profile(account_id: str) -> dict:
    """Get basic profile of an account and its owner"""
    accounts  = pd.read_csv("data/raw/accounts.csv")
    customers = pd.read_csv("data/raw/customers.csv")
    companies = pd.read_csv("data/raw/companies.csv")

    acc = accounts[accounts["account_id"] == account_id]
    if acc.empty:
        return {"error": "account not found"}

    acc = acc.iloc[0]
    owner_id = acc["owner_id"]

    owner_info = {}
    cust = customers[customers["customer_id"] == owner_id]
    if not cust.empty:
        c = cust.iloc[0]
        owner_info = {
            "type"       : "individual",
            "name"       : c["name"],
            "occupation" : c["occupation"],
            "kyc_status" : c["kyc_status"],
            "risk_label" : c["risk_label"]
        }
    else:
        comp = companies[companies["company_id"] == owner_id]
        if not comp.empty:
            co = comp.iloc[0]
            owner_info = {
                "type"     : "company",
                "name"     : co["company_name"],
                "industry" : co["industry"],
                "country"  : co["country"]
            }

    return {
        "account_id"   : account_id,
        "account_type" : acc["account_type"],
        "balance"      : acc["balance"],
        "currency"     : acc["currency"],
        "status"       : acc["status"],
        "owner"        : owner_info
    }

def tool_get_connections(account_id: str) -> dict:
    """Get all entities connected to this account in the graph"""
    driver = get_driver()
    if not driver:
        return {"error": "could not connect to Neo4j"}

    with driver.session() as s:
        result = s.run("""
            MATCH (a:Account {account_id: $account_id})-[r*1..2]-(connected)
            RETURN DISTINCT labels(connected) AS type,
                   connected.account_id  AS account_id,
                   connected.customer_id AS customer_id,
                   connected.company_id  AS company_id,
                   connected.name        AS name,
                   connected.alert_id    AS alert_id,
                   connected.reason      AS alert_reason
            LIMIT 20
        """, account_id=account_id)

        connections = []
        for record in result:
            entry = {"type": record["type"]}
            if record["name"]:
                entry["name"] = record["name"]
            if record["account_id"]:
                entry["account_id"] = record["account_id"]
            if record["customer_id"]:
                entry["customer_id"] = record["customer_id"]
            if record["company_id"]:
                entry["company_id"] = record["company_id"]
            if record["alert_id"]:
                entry["alert_id"]    = record["alert_id"]
                entry["alert_reason"] = record["alert_reason"]
            connections.append(entry)

    driver.close()
    return {
        "account_id"  : account_id,
        "total_found" : len(connections),
        "connections" : connections
    }

def tool_get_risk_score(account_id: str) -> dict:
    """Get risk score and explanation for an account"""
    score   = predict_risk(account_id)
    
    # check for errors before accessing keys
    if "error" in score:
        return {"error": score["error"], "account_id": account_id}

    explain = explain_risk(account_id)

    return {
        "account_id"         : account_id,
        "risk_score"         : score.get("risk_score", 0),
        "risk_level"         : score.get("risk_level", "Unknown"),
        "top_reasons"        : score.get("reasons", []),
        "risk_factors"       : explain.get("risk_factors", []),
        "protective_factors" : explain.get("protective_factors", [])
    }

def tool_get_transaction_summary(account_id: str) -> dict:
    """Get transaction history summary for an account"""
    transactions = pd.read_csv("data/raw/transactions.csv")
    alerts       = pd.read_csv("data/raw/alerts.csv")

    sent     = transactions[transactions["sender_account"]   == account_id]
    received = transactions[transactions["receiver_account"] == account_id]

    suspicious_sent = sent[sent["is_suspicious"] == True]

    account_alerts = alerts[alerts["account_flagged"] == account_id]

    return {
        "account_id"            : account_id,
        "total_sent"            : len(sent),
        "total_received"        : len(received),
        "total_amount_sent"     : round(sent["amount"].sum(), 2),
        "total_amount_received" : round(received["amount"].sum(), 2),
        "suspicious_txns"       : len(suspicious_sent),
        "international_txns"    : len(sent[sent["type"] == "SWIFT"]),
        "unique_receivers"      : sent["receiver_account"].nunique(),
        "active_alerts"         : len(account_alerts),
        "alert_reasons"         : account_alerts["reason"].tolist()
    }

# tool definitions for Claude API
TOOL_DEFINITIONS = [
    {
        "name"        : "get_account_profile",
        "description" : "Get the basic profile of an account including owner details and KYC status",
        "input_schema": {
            "type"      : "object",
            "properties": {
                "account_id": {
                    "type"       : "string",
                    "description": "The account ID to look up"
                }
            },
            "required": ["account_id"]
        }
    },
    {
        "name"        : "get_connections",
        "description" : "Get all entities connected to this account in the knowledge graph — customers, companies, other accounts, alerts",
        "input_schema": {
            "type"      : "object",
            "properties": {
                "account_id": {
                    "type"       : "string",
                    "description": "The account ID to find connections for"
                }
            },
            "required": ["account_id"]
        }
    },
    {
        "name"        : "get_risk_score",
        "description" : "Get the ML risk score and SHAP explanation for why this account scored that way",
        "input_schema": {
            "type"      : "object",
            "properties": {
                "account_id": {
                    "type"       : "string",
                    "description": "The account ID to score"
                }
            },
            "required": ["account_id"]
        }
    },
    {
        "name"        : "get_transaction_summary",
        "description" : "Get a summary of transaction history, suspicious transactions, and active alerts for an account",
        "input_schema": {
            "type"      : "object",
            "properties": {
                "account_id": {
                    "type"       : "string",
                    "description": "The account ID to summarise"
                }
            },
            "required": ["account_id"]
        }
    }
]

def run_tool(tool_name: str, tool_input: dict) -> dict:
    """Route tool calls from the agent to the right function"""
    if tool_name == "get_account_profile":
        return tool_get_account_profile(tool_input["account_id"])
    elif tool_name == "get_connections":
        return tool_get_connections(tool_input["account_id"])
    elif tool_name == "get_risk_score":
        return tool_get_risk_score(tool_input["account_id"])
    elif tool_name == "get_transaction_summary":
        return tool_get_transaction_summary(tool_input["account_id"])
    else:
        return {"error": f"unknown tool {tool_name}"}