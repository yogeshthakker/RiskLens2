# RiskLens

### AI Copilot for Banking Risk Investigation

RiskLens is a banking risk investigation platform designed to help analysts assess potentially suspicious accounts by combining machine learning-based risk scoring, explainable AI, transaction analysis, graph-based entity relationships, and AI-assisted investigation reports.

The system takes an account ID as input and provides a consolidated view of its risk level, key risk factors, transaction behaviour, connected entities, and recommended investigative actions.

---

## Overview

Traditional risk monitoring systems may identify suspicious accounts, but understanding **why an account is considered risky** often requires analysts to manually examine multiple sources of information.

RiskLens brings these investigation steps together into a single workflow:

**Account → Risk Score → Risk Factors → Transactions → Connected Entities → Investigation Report**

The objective is not only to generate a risk score, but also to provide supporting context that can help an analyst investigate the account further.

---

## Key Features

### 1. Account Risk Scoring

RiskLens uses an XGBoost classification model to generate an account-level risk probability.

The probability is converted into a risk score from **0–100** and classified as:

- **Low:** Risk score < 40
- **Medium:** Risk score 40–69.9
- **High:** Risk score ≥ 70

The model uses transaction behaviour, account status, alerts, and KYC-related indicators as input features.

---

### 2. Explainable Risk Analysis

RiskLens uses **SHAP (SHapley Additive exPlanations)** to explain the model's prediction.

The system identifies:

- Factors that increase risk
- Factors that reduce risk
- The value of each feature
- The corresponding feature impact

This allows the system to provide more context behind the risk score instead of presenting it as a black-box prediction.

---

### 3. Transaction Behaviour Analysis

The system analyses transaction history for an account, including:

- Total number of transactions
- Total transaction amount
- Average transaction amount
- Transaction spikes
- International transactions
- Unique receivers
- Suspicious transactions
- Cash transaction activity
- Active account alerts

These behavioural signals are transformed into features used by the machine learning model.

---

### 4. Graph-Based Entity Investigation

RiskLens uses **Neo4j** to represent relationships between financial entities.

The graph contains entities such as:

- Customers
- Companies
- Accounts
- Alerts

Relationships include:

- Customer → Account
- Customer → Company
- Company → Account
- Account → Account
- Account → Alert

This enables investigators to identify accounts and entities connected to the account under investigation.

---

### 5. AI-Assisted Investigation Reports

RiskLens includes an AI investigation agent that gathers information from multiple sources before generating a structured investigation report.

The agent collects:

1. Account profile
2. Transaction summary
3. Connected entities
4. Machine learning risk score
5. Explainable risk factors

It then generates a report containing:

- Entity information
- Account information
- Risk score
- Observations
- Connected entities
- Recommended next steps

The report generation workflow is designed to provide analysts with a concise summary of the available evidence.

---

## Machine Learning Pipeline

The machine learning pipeline begins with account, customer, transaction, and alert data.

### Feature Engineering

RiskLens generates 13 features for each account:

| Feature | Description |
|---|---|
| `total_txns` | Total number of transactions |
| `total_amount` | Total transaction amount |
| `avg_amount` | Average transaction amount |
| `spike_ratio` | Recent transaction activity compared with older activity |
| `intl_ratio` | Ratio of international/SWIFT transactions |
| `unique_receivers` | Number of unique receiving accounts |
| `suspicious_ratio` | Ratio of suspicious transactions |
| `cash_ratio` | Ratio of cash transactions |
| `has_alert` | Whether the account has an active alert |
| `is_frozen` | Whether the account is frozen |
| `is_dormant` | Whether the account is dormant |
| `kyc_flagged` | Whether the owner's KYC status is flagged |
| `kyc_pending` | Whether the owner's KYC status is pending |

The generated features are stored in:

`data/processed/features.csv`

---

## Risk Model

RiskLens uses an **XGBoost Classifier** for account risk prediction.

The model is trained using the engineered account-level features and produces a probability representing the likelihood of an account belonging to the suspicious class.

The current training pipeline uses an 80/20 train-test split.

Model configuration includes:

- XGBoost Classifier
- 100 estimators
- Maximum depth: 4
- Learning rate: 0.1
- Random state: 42

The trained model is stored as:

`warning_engine/models/xgb_model.pkl`

---

## Explainability with SHAP

After generating a prediction, RiskLens uses SHAP TreeExplainer to analyse the model output.

The system separates the most influential features into:

### Risk Increasing Factors

Features with positive SHAP impact are identified as factors contributing to higher predicted risk.

### Protective Factors

Features with negative SHAP impact are identified as factors contributing to lower predicted risk.

The interface presents these factors directly alongside the risk score.

---

## Graph Data Model

The Neo4j graph represents the relationships within the banking ecosystem.

Example structure:

```text
Customer
   │
   ├── LINKED_TO ──> Account
   │
   └── OWNS ───────> Company
                         │
                         └── LINKED_TO ──> Account

Account
   │
   ├── TRANSFERS_TO ──> Account
   │
   └── HAS_ALERT ─────> Alert
