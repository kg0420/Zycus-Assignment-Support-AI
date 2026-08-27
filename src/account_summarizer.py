import json

from google import genai

from src.config import GEMINI_API_KEY
import hashlib
from pathlib import Path

client = genai.Client(
    api_key=GEMINI_API_KEY
)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
MODEL_NAME = "gemini-2.5-flash"


SYSTEM_PROMPT = """
You are an enterprise Customer Success / TAM assistant.

Your job is to analyze an account health snapshot and create a
concise QBR preparation brief.

The input contains:
- account information
- account-level health metrics
- account escalation notes
- tickets from the last 90 days
- ticket-derived metrics
- churn evidence
- escalation evidence

You MUST use only the information provided in the snapshot.

Do not invent facts.

Do not invent ticket IDs.

Do not invent customer quotes.

Do not invent churn or escalation evidence.

IMPORTANT:

Account-level escalation notes and ticket-level evidence are
different sources.

If a risk comes from an account escalation note, clearly identify
it as an account-level signal.

If a risk is supported by a ticket, include the exact ticket quote.

Every ticket-based churn or escalation risk MUST include:
- ticket_id
- exact quote from the ticket

The final output must contain exactly three sections:

1. executive_summary
2. open_risks
3. tam_talking_points

EXECUTIVE SUMMARY

Write 3-5 concise sentences describing the current account health.

OPEN RISKS

Identify meaningful risks such as:
- churn
- escalation
- unresolved support problems
- poor customer satisfaction
- declining usage
- renewal concerns

Only include risks supported by evidence.

TAM TALKING POINTS

Provide practical points the TAM should discuss during the QBR.

Talking points should be specific to the account and evidence,
not generic customer-success advice.

Do not claim that something is a problem merely because another
field suggests it indirectly.

Be concise and professional.
"""

def get_cache_key(snapshot: dict) -> str:

    content = json.dumps(
        snapshot,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

def build_account_prompt(snapshot: dict) -> str:

    return f"""
Analyze the following account snapshot.

ACCOUNT SNAPSHOT
================

{json.dumps(
    snapshot,
    indent=2,
    ensure_ascii=False
)}


Return ONLY valid JSON using this structure:

{{
    "executive_summary": "3-5 sentence summary",

    "open_risks": [
        {{
            "risk_type": "string",
            "severity": "High | Medium | Low",
            "description": "string",
            "evidence_source": "account | ticket",
            "evidence":"supporting evidence",
            "ticket_id": "string or null",
            "quote": "exact ticket quote or null"
        }}
    ],

    "tam_talking_points": [
        "talking point 1",
        "talking point 2",
        "talking point 3"
    ]
}}
""".strip()


def summarize_account(
    snapshot: dict
) -> dict:

    cache_key = get_cache_key(
        snapshot
    )

    cache_file = (
        CACHE_DIR /
        f"{cache_key}.json"
    )

    # ---------------------------------------------------------
    # Use cached Gemini response
    # ---------------------------------------------------------

    if cache_file.exists():

        with open(
            cache_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    # ---------------------------------------------------------
    # Call Gemini
    # ---------------------------------------------------------

    prompt = build_account_prompt(
        snapshot
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text":
                            SYSTEM_PROMPT
                            + "\n\n"
                            + prompt
                    }
                ]
            }
        ],
        config={
            "temperature": 0
        }
    )

    text = response.text.strip()

    # Remove markdown fences
    if text.startswith("```json"):

        text = text[
            len("```json"):
        ].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

    elif text.startswith("```"):

        text = text[3:].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

    result = json.loads(text)

    # ---------------------------------------------------------
    # Save Gemini response
    # ---------------------------------------------------------

    with open(
        cache_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    return result