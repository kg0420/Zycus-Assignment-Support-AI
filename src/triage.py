import json
from typing import List

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY
from src.models import TriageResult
from src.retrieval import KnowledgeBaseRetriever
from src.rules import validate_triage
from src.rules import (
    validate_triage,
    infer_category_from_ticket,
    infer_urgency_from_ticket,
)
client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-2.5-flash-lite"


SYSTEM_PROMPT = """
You are an intelligent enterprise support ticket triage agent.

Analyze the customer's support ticket and produce a structured
triage decision.

PRODUCT AREA
------------
Identify the relevant product area from the ticket.

CATEGORY
--------
The category MUST be exactly one of:

- Feature Request
- How-To
- Performance
- Billing
- Integration
- Onboarding
- Data Loss

Do NOT invent a new category.

For example:
- SSO is a product area, NOT a category.
- Authentication is a product area/topic, NOT a category.
- An SSO configuration/API connection problem may be categorized
  as Integration when the customer is trying to connect systems.
- A documentation/configuration question may be How-To.

URGENCY
-------
P1 = critical / business stopped
P2 = major impact / significant workaround required
P3 = moderate impact / workaround available
P4 = low impact / cosmetic / minor

Use evidence from the customer's actual ticket.

KNOWN ISSUE
-----------
Only mark known_issue=true when the supplied knowledge base
contains information that directly supports the issue, error,
or documented behavior.

A merely related KB document is NOT sufficient evidence.

KNOWLEDGE BASE
--------------
Only reference documents actually supplied in the knowledge base.

Do not invent document names, sections, errors, solutions,
or product behavior.

REASONING
---------
Give concise reasoning based on evidence in the ticket and
retrieved knowledge base.

FIRST RESPONSE
--------------
Write a concise first-response draft for the customer.

Rules:
- Do NOT include "Subject:".
- Do NOT include "Dear Customer".
- Do NOT include a signature.
- Do NOT include "Sincerely".
- Acknowledge the issue.
- Mention the impact when relevant.
- Give troubleshooting steps ONLY if they are explicitly supported
  by the supplied knowledge base.
- Do not invent technical explanations.
- Do not claim that a solution will definitely resolve the issue.
- If the knowledge base does not provide a verified solution,
  say that the support team will investigate.
- Keep the response professional and concise.
"""


def build_ticket_text(ticket: dict) -> str:

    return f"""
Ticket ID:
{ticket.get("ticket_id", "unknown")}

Subject:
{ticket.get("subject", "")}

Body:
{ticket.get("body", "")}

Product:
{ticket.get("product", "")}

Product Area:
{ticket.get("product_area", "")}

Existing Category:
{ticket.get("category", "")}

Existing Urgency:
{ticket.get("urgency", "")}

Plan:
{ticket.get("plan_tier", "")}
""".strip()


def build_kb_context(results: List[dict]) -> str:

    if not results:
        return "No relevant knowledge-base documents were retrieved."

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
SOURCE: {result["source"]}

{result["text"]}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)



import re


def extract_error_codes(text: str) -> list[str]:

    patterns = [
        r"\b[A-Z][A-Z0-9_]+(?:_[A-Z0-9]+)+\b",
        r"\b\d{3}\s+(?:Forbidden|Unauthorized|Not Found|Internal Server Error)\b",
    ]

    matches = []

    for pattern in patterns:
        matches.extend(
            re.findall(pattern, text)
        )

    return list(dict.fromkeys(matches))

def triage_ticket(
    ticket: dict,
    retriever: KnowledgeBaseRetriever
) -> TriageResult:

    ticket_text = build_ticket_text(ticket)

    error_codes = extract_error_codes(
    ticket.get("body", "")
)

    retrieval_query = f"""
        Product: {ticket.get("product", "")}
        Product Area: {ticket.get("product_area", "")}
        Subject: {ticket.get("subject", "")}
        Error Codes: {" ".join(error_codes)}
        Issue:
        {ticket.get("body", "")}
        """.strip()

    kb_results = retriever.search(
        retrieval_query,
        top_k=3
    )

    kb_context = build_kb_context(kb_results)

    prompt = f"""
{SYSTEM_PROMPT}

TICKET
======

{ticket_text}


KNOWLEDGE BASE
==============

{kb_context}


Return ONLY valid JSON with this structure:

{{
    "product_area": "string",
    "category": "string",
    "urgency": "P1",
    "reasoning": "string",
    "known_issue": true,
    "knowledge_base_docs": [
        {{
            "source": "string",
            "section": "string or null",
            "relevance": 0.0
        }}
    ],
    "recommended_team": "string",
    "first_response": "string"
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    content = response.text

    data = json.loads(content)

    result= TriageResult.model_validate(data)
    # ---------------------------------------------------------
    # Deterministic high-confidence overrides
    # ---------------------------------------------------------

    category_override = infer_category_from_ticket(
        ticket
    )

    if category_override:
        result.category = category_override


    urgency_override = infer_urgency_from_ticket(
        ticket
    )

    if urgency_override:
        result.urgency = urgency_override
        
    result= validate_triage(result)
    return result