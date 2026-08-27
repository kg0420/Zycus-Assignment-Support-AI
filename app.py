from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.account_health import (
    load_json,
    build_account_snapshot,
)

from src.account_summarizer import (
    summarize_account,
)

from src.config import (
    ACCOUNTS_FILE,
    TICKETS_FILE,
    KB_DIR,
)

from src.models import (
    TriageResult,
)

from src.retrieval import (
    KnowledgeBaseRetriever,
)

from src.triage import (
    triage_ticket,
)


# ============================================================
# Application
# ============================================================

app = FastAPI(
    title="Support AI Assistant",
    description=(
        "AI-powered support ticket triage and "
        "account health summarization."
    ),
    version="1.0.0",
)


# ============================================================
# Load data once when application starts
# ============================================================

accounts = load_json(
    ACCOUNTS_FILE
)

tickets = load_json(
    TICKETS_FILE
)

retriever = KnowledgeBaseRetriever(
    KB_DIR
)


# ============================================================
# Request Models
# ============================================================

class TicketRequest(BaseModel):
    ticket_id: str | None = None
    account_id: str | None = None
    company: str | None = None
    subject: str
    body: str
    product: str
    product_area: str
    plan_tier: str


class AccountHealthResponse(BaseModel):
    account_id: str
    executive_summary: str
    open_risks: list[dict]
    tam_talking_points: list[str]


# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health"
)
def health_check():

    return {
        "status": "ok",
        "service": "support-ai"
    }


# ============================================================
# Task 1 — Ticket Triage
# ============================================================

@app.post(
    "/triage",
    response_model=TriageResult
)
def triage(
    request: TicketRequest
):

    try:

        ticket = request.model_dump()

        result = triage_ticket(
            ticket,
            retriever
        )

        return result

    except Exception as exc:

        if is_rate_limit_error(exc):

            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_QUOTA_EXCEEDED",
                    "message": (
                        "The AI service quota has been "
                        "exceeded. Please retry later."
                    )
                }
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TRIAGE_FAILED",
                "message": str(exc)
            }
        )
    
# ============================================================
# Task 2 — Account Health
# ============================================================

@app.get(
    "/accounts/{account_id}/health",
    response_model=AccountHealthResponse
)
def account_health(
    account_id: str
):

    # --------------------------------------------------------
    # Validate account
    # --------------------------------------------------------

    account_exists = any(
        account.get("account_id")
        == account_id
        for account in accounts
    )

    if not account_exists:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "ACCOUNT_NOT_FOUND",
                "account_id": account_id
            }
        )

    # --------------------------------------------------------
    # Build deterministic snapshot
    # --------------------------------------------------------

    try:

        snapshot = build_account_snapshot(
            accounts,
            tickets,
            account_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    # --------------------------------------------------------
    # Generate Gemini summary
    # --------------------------------------------------------

    try:

        summary = summarize_account(
            snapshot
        )

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": (
                    "Account health data was "
                    "retrieved, but the AI summary "
                    "could not be generated."
                ),
                "reason": str(exc)
            }
        )

    # --------------------------------------------------------
    # Return final response
    # --------------------------------------------------------

    return {
        "account_id": account_id,
        "executive_summary": summary.get(
            "executive_summary",
            ""
        ),
        "open_risks": summary.get(
            "open_risks",
            []
        ),
        "tam_talking_points": summary.get(
            "tam_talking_points",
            []
        )
    }   

def is_rate_limit_error(
    exc: Exception
) -> bool:

    message = str(exc).lower()

    return (
        "429" in message
        or "resource_exhausted" in message
        or "quota" in message
    )