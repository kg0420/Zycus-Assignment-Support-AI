import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import TICKETS_FILE, KB_DIR
from src.retrieval import KnowledgeBaseRetriever
from src.triage import triage_ticket


app = FastAPI(
    title="Support AI",
    version="1.0.0"
)


retriever = KnowledgeBaseRetriever(KB_DIR)


class TicketRequest(BaseModel):

    subject: str
    body: str

    product: str | None = None
    product_area: str | None = None
    plan_tier: str | None = None


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/triage")
def triage(request: TicketRequest):

    ticket = {
        "subject": request.subject,
        "body": request.body,
        "product": request.product or "",
        "product_area": request.product_area or "",
        "plan_tier": request.plan_tier or "",
    }

    try:

        result = triage_ticket(
            ticket,
            retriever
        )

        return result.model_dump()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )