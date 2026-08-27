# Support AI — Technical Support & TAM Assistant

An AI-powered support assistant designed to help Technical Support and Technical Account Management (TAM) teams automate support ticket triage and customer account health analysis.

The system combines deterministic Python logic, knowledge-base retrieval, and Google Gemini to produce structured, explainable outputs.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Task 1 — Ticket Triage](#task-1--ticket-triage)
- [Task 2 — TAM Account Health](#task-2--tam-account-health)
- [Evaluation](#evaluation)
- [Knowledge Base Retrieval](#knowledge-base-retrieval)
- [Deterministic Rules](#deterministic-rules)
- [Error Handling](#error-handling)
- [Data Handling & Security](#data-handling--security)
- [Design Note](#design-note)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Submission Checklist](#submission-checklist)

---

# Overview

Support teams need to process a large number of customer tickets while maintaining consistent prioritization, routing, and responses.

At the same time, TAMs need a concise view of customer account health by reviewing account attributes, recent support history, churn signals, escalation signals, and upcoming renewals.

This project provides two AI-assisted workflows:

### 1. Support Ticket Triage

Given a support ticket, the system determines:

- Product area
- Category
- Urgency (P1–P4)
- Reasoning
- Known-issue status
- Relevant knowledge-base documents
- Recommended support team
- Draft first response

### 2. TAM Account Health

Given an account ID, the system:

- Retrieves account information
- Filters support tickets to the last 90 days
- Calculates ticket metrics
- Identifies churn evidence
- Identifies escalation evidence
- Detects data-quality inconsistencies
- Generates an executive summary
- Generates open-risk items
- Generates TAM talking points

---

# Problem Statement

The system addresses two operational problems.

## Support Operations

Support agents need to quickly understand:

- What the customer is reporting
- How urgent the issue is
- Which team should handle it
- Whether a known solution exists
- What response should be sent to the customer

## Account Management

TAMs need to understand:

- Current customer health
- Recent support activity
- Churn indicators
- Escalation indicators
- Renewal risk
- Customer-facing discussion points

The goal is to reduce manual analysis while keeping outputs structured, grounded, and explainable.

---

# Solution

The solution uses a hybrid architecture combining deterministic processing, retrieval, and LLM reasoning.

```text
                         Support AI
                             |
              +--------------+--------------+
              |                             |
              v                             v
       Ticket Triage                 Account Health
              |                             |
       +------+-------+             +-------+-------+
       |              |             |               |
       v              v             v               v
  Python Rules     Gemini       Account Data    Ticket Data
       |              |             |               |
       +------+-------+             +-------+-------+
              |                             |
              v                             v
       KB Retrieval                 90-Day Filtering
              |                             |
              v                             v
        Triage Result               Account Snapshot
                                            |
                                            v
                                         Gemini
                                            |
                                            v
                                  QBR Health Summary
```

The system does not rely on the LLM for calculations that can be performed deterministically.

Examples include:

- 90-day ticket filtering
- Ticket counts
- Open-ticket counts
- P1 counts
- Renewal-date calculations
- Account lookup
- High-confidence classification rules

Gemini is primarily used for reasoning and natural-language synthesis.

---

# Key Features

## Ticket Triage

- Structured ticket classification
- P1–P4 urgency classification
- Category classification
- Product-area identification
- Knowledge-base retrieval
- Known-issue identification
- Recommended team
- Customer-facing first response
- Pydantic schema validation

## Account Health

- Account lookup
- 90-day ticket filtering
- Open-ticket metrics
- P1 metrics
- Low-CSAT identification
- Churn evidence
- Escalation evidence
- Account-level escalation notes
- Data-quality discrepancy detection
- Executive summary
- Open risks
- TAM talking points

## Reliability

- Deterministic business rules
- Structured LLM output
- API error handling
- Missing-account handling
- Gemini quota/rate-limit handling
- Development-time response caching

## Evaluation

- Task 1 evaluation cases
- Task 2 evaluation cases
- Pass/fail scoring
- 0–1 quality scores
- Adversarial test cases
- Evaluation report generation
- API quota failures reported separately from logical failures

---

# Architecture

## Ticket Triage Flow

```text
Raw Ticket
    |
    v
Input Validation
    |
    v
High-Confidence Python Rules
    |
    +----------------------+
    |                      |
    | Clear Case           | Ambiguous Case
    v                      v
Deterministic Rule       Gemini
    |                      |
    +----------+-----------+
               |
               v
       Knowledge Base
          Retrieval
               |
               v
        Final Triage
               |
               v
       Structured JSON
```

## Account Health Flow

```text
Account ID
    |
    v
Account Lookup
    |
    v
Retrieve Account
    |
    v
Filter Tickets
to Last 90 Days
    |
    v
Calculate Metrics
    |
    +-------------------+
    |                   |
    v                   v
Churn Signals      Escalation Signals
    |                   |
    +---------+---------+
              |
              v
       Account Snapshot
              |
              v
            Gemini
              |
              v
    +---------+---------+
    |         |         |
    v         v         v
Executive   Open      TAM
Summary     Risks     Talking Points
```

---

# Project Structure

```text
Zycus_Task/
│
├── data/
│   ├── accounts.json
│   └── tickets.json
│
├── knowledge-base/
│   ├── products/
│   ├── troubleshooting/
│   ├── billing/
│   └── onboarding/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── retrieval.py
│   ├── rules.py
│   ├── triage.py
│   ├── account_health.py
│   ├── account_summarizer.py
│   └── data_quality.py
│
├── evals/
│   ├── evaluator.py
│   ├── run_evals.py
│   ├── task1_cases.json
│   └── task2_cases.json
│
├── app.py
├── main.py
├── DESIGN.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

# Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| LLM | Google Gemini |
| Retrieval | BM25 |
| Data Validation | Pydantic |
| Configuration | python-dotenv |
| Server | Uvicorn |
| Input Data | JSON |
| Knowledge Base | Markdown |
| Evaluation | Custom Python evaluation harness |

---

# Prerequisites

- Python 3.10 or newer
- Google Gemini API key
- Windows, macOS, or Linux

---

# Installation

## 1. Clone the repository

```bash
git clone (https://github.com/kg0420/Zycus-Assignment-Support-AI.git)
cd Zycus_Task
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

A template is provided as:

```text
.env.example
```

Example:

```env
GEMINI_API_KEY=
```

## Security

Never commit:

```text
.env
API keys
Access tokens
Passwords
Credentials
```

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
cache/
```

---

# Running the Application

## CLI

Run the account-health demonstration:

```bash
python main.py
```

The CLI loads the account and ticket datasets, builds the account snapshot, and generates the QBR-style health summary.

---

# Running the REST API

Start the FastAPI application:

```bash
uvicorn app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "support-ai"
}
```

---

# Task 1 — Ticket Triage

## Endpoint

```http
POST /triage
```

## Request

Example:

```json
{
  "ticket_id": "TEST-001",
  "account_id": "ACC-3336",
  "company": "Omni Consumer Products",
  "subject": "Production SSO outage",
  "body": "Our production SSO is completely unavailable. All employees are unable to log in and business operations are blocked.",
  "product": "SecureVault",
  "product_area": "SSO",
  "plan_tier": "Enterprise"
}
```

## Expected Output

```json
{
  "product_area": "SSO",
  "category": "Integration",
  "urgency": "P1",
  "reasoning": "The customer reports a complete production SSO outage...",
  "known_issue": false,
  "knowledge_base_docs": [],
  "recommended_team": "Technical Support",
  "first_response": "We understand that your production SSO is completely unavailable..."
}
```

## Classification Examples

```text
Production SSO outage
        ↓
Integration + P1

Invoice / billing discrepancy
        ↓
Billing + P4

Explicit How-To request
        ↓
How-To + P4

New users unable to authenticate through SSO
        ↓
Integration + P2/P3
```

The system uses deterministic rules for high-confidence scenarios and Gemini for reasoning where the case is less obvious.

---

# Task 2 — TAM Account Health

## Endpoint

```http
GET /accounts/{account_id}/health
```

Example:

```http
GET /accounts/ACC-3336/health
```

## Output

The response contains:

```text
Executive Summary
Open Risks
TAM Talking Points
```

The account-health workflow also retains the structured account snapshot used to generate the summary.

---

# Example Account

For:

```text
ACC-3336
```

the account data includes:

```text
Health Status : At Risk
Usage Trend   : Inactive
Open Tickets  : 7
ARR           : $500,000
Renewal Date  : 2026-08-19
```

The account also contains escalation notes indicating:

```text
3 consecutive P1 tickets in the last 30 days
Decision maker considering competing vendor evaluation
```

The system surfaces these as account-level risk signals and can identify a discrepancy if structured ticket metrics disagree with the account-level escalation notes.

---

# 90-Day Ticket Analysis

Ticket filtering is performed in Python using the ticket creation date.

The workflow calculates:

```text
Total tickets
Open tickets
P1 tickets
Low-CSAT tickets
```

It also separates:

```text
Open tickets
P1 tickets
Low-CSAT tickets
Churn evidence
Escalation evidence
```

Tickets reference accounts using `account_id`. Missing account relationships are handled gracefully.

---

# Knowledge Base Retrieval

The ticket-triage workflow uses BM25 retrieval over the knowledge base.

The retrieval layer returns:

```text
Source
Section
Relevance score
Text
```

Example:

```json
{
  "source": "authentication-sso.md",
  "section": "New Users Cannot Authenticate via SSO",
  "relevance": 1.0
}
```

Knowledge-base retrieval is used to ground known-issue identification and troubleshooting responses.

---

# Deterministic Rules

A hybrid LLM + rules approach is used.

## Billing

Signals may include:

```text
invoice
charged
billing
payment
subscription
```

## Integration

Signals may include:

```text
SSO
SAML
identity provider
IDP
integration
connector
```

## Critical Issues

Signals may include:

```text
production outage
production completely unavailable
business operations blocked
complete outage
```

The purpose of these rules is to provide predictable behavior for high-confidence cases and reduce unnecessary LLM calls.

---

# Error Handling

The application distinguishes between several failure types.

## Account Not Found

Example:

```json
{
  "error": "ACCOUNT_NOT_FOUND",
  "account_id": "ACC-DOES-NOT-EXIST"
}
```

## AI Service Unavailable

If Gemini is unavailable or its quota is exhausted, the application returns an appropriate service-unavailable response rather than treating the external failure as an application logic failure.

Example:

```json
{
  "error": "AI_SERVICE_UNAVAILABLE",
  "message": "Account health data was retrieved, but the AI summary could not be generated."
}
```

---

# Evaluation

Run:

```bash
python -m evals.run_evals
```

The evaluation harness contains separate cases for Task 1 and Task 2.

Each case evaluates:

```text
Expected output
        ↓
Actual output
        ↓
Individual checks
        ↓
0–1 score
        ↓
PASS / FAIL
```

The final report is saved as:

```text
eval_report.json
```

---

# Current Evaluation Result

The latest successful Task 1 evaluation achieved:

```text
Task 1
Passed: 5/5
Average score: 1.0
```

Task 1 currently covers:

- Critical production outage
- Performance issue
- How-To question
- Billing question
- Ambiguous authentication issue

Task 2 includes:

- At-risk account
- Multiple account-specific cases
- Missing account handling
- Account-health analysis

### Gemini Free-Tier Note

During development, some Task 2 evaluation cases may fail temporarily when the Gemini free-tier request quota is exhausted.

For example:

```text
429 RESOURCE_EXHAUSTED
generate_content_free_tier_requests
```

This is an external API quota limitation, not a deterministic application logic failure.

The evaluation harness reports these external failures separately.

---

# Adversarial Testing

The evaluation suite includes adversarial scenarios.

## Task 1

An SSO ticket that is actually asking for configuration instructions should remain a How-To request rather than automatically becoming an Integration issue.

## Task 2

The account data can contain conflicting information such as:

```text
Structured metric:
P1 tickets = 0

Escalation note:
3 consecutive P1 tickets
```

The system surfaces this as a data-quality discrepancy instead of silently choosing one source.

---

# Data Handling & Security

The supplied dataset is synthetic and is used only for this assignment.

Credentials are loaded through environment variables.

The repository should never contain the actual Gemini API key.

For a production deployment, additional controls would be required:

- PII detection
- PII redaction
- Data minimization
- Authentication
- Authorization
- Audit logging
- Encrypted transport
- Secure secret management

Only the minimum information required for the LLM task should be sent to an external model provider.

---

# Design Note

Detailed production-design considerations are documented separately in:

```text
DESIGN.md
```

The design note covers:

1. Failure modes
2. Latency vs quality trade-offs
3. Data sensitivity
4. Scaling considerations

---

# Limitations

This project is a prototype designed around the supplied mock dataset.

Current limitations include:

- Local JSON data storage
- Local BM25 retrieval
- External Gemini dependency
- Gemini free-tier quota limitations
- No production authentication layer
- No distributed task queue
- No production database
- No production-grade observability
- Limited evaluation dataset size

These limitations are intentional for the scope of the assignment.

---

# Future Improvements

## Retrieval

- Persistent retrieval index
- Hybrid BM25 + vector search
- Retrieval-quality evaluation
- Metadata filtering

## LLM

- Model fallback
- Prompt versioning
- Structured generation
- Token/cost monitoring
- LLM response caching

## API

- Authentication
- Authorization
- Rate limiting
- Async processing
- Background jobs

## Data

- PostgreSQL or another production database
- Data validation pipeline
- PII detection/redaction

## Observability

- Request tracing
- Latency metrics
- Token usage
- Error monitoring
- Retrieval metrics
- Evaluation regression monitoring

---

# Production Scaling Strategy

At larger volumes, likely bottlenecks include:

```text
LLM request volume
API rate limits
Retrieval latency
Repeated account calculations
Application memory
```

A scalable architecture could introduce:

```text
                    API
                     |
              Load Balancer
                     |
          +----------+----------+
          |                     |
       API Worker           API Worker
          |                     |
          +----------+----------+
                     |
                Task Queue
                     |
          +----------+----------+
          |                     |
     Retrieval Worker      LLM Worker
          |                     |
          +----------+----------+
                     |
                Cache / DB
```

Frequently requested summaries and repeated classifications can be cached, while expensive LLM operations can be processed asynchronously.

---

# Local Development Commands

## Run CLI

```bash
python main.py
```

## Run API

```bash
uvicorn app:app --reload
```

## Run Evaluation

```bash
python -m evals.run_evals
```

## Open Swagger

```text
http://127.0.0.1:8000/docs
```

---

# Submission Checklist

Before submitting the repository:

- [ ] `README.md` included
- [ ] `DESIGN.md` included
- [ ] `requirements.txt` included
- [ ] `.env.example` included
- [ ] Real `.env` excluded
- [ ] Gemini API key removed from all source files
- [ ] `python main.py` works
- [ ] `pip install -r requirements.txt` works
- [ ] FastAPI starts successfully
- [ ] `/health` works
- [ ] `/triage` works
- [ ] `/accounts/{account_id}/health` works
- [ ] Task 1 evaluation included
- [ ] Task 2 evaluation included
- [ ] Adversarial cases included
- [ ] `eval_report.json` generated
- [ ] No credentials committed
- [ ] GitHub repository checked before submission
- [ ] 3–6 minute Loom walkthrough prepared

---

# Author

**Krish Gupta**

Support AI — Technical Support & TAM Assistant

Built as a technical assessment demonstrating:

- LLM integration
- Retrieval-Augmented Generation
- Deterministic business rules
- Structured outputs
- Account health analysis
- API development
- Evaluation design
- Production-oriented system design
