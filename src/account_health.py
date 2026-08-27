from datetime import datetime, timedelta

from src.config import ANALYSIS_DATE
from src.data_quality import check_account_consistency


CHURN_KEYWORDS = [
    "competitor",
    "competing vendor",
    "switching",
    "switch",
    "cancel",
    "cancellation",
    "churn",
    "replace",
    "replacing",
    "alternative vendor",
    "another vendor",
    "considering leaving",
]


ESCALATION_KEYWORDS = [
    "escalate",
    "escalation",
    "critical",
    "business continuity",
    "production blocked",
    "production outage",
    "urgent",
    "unacceptable",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        import json
        return json.load(f)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "")
    )


def get_account(
    accounts: list[dict],
    account_id: str
):
    for account in accounts:

        if account.get("account_id") == account_id:
            return account

    return None


def get_account_tickets(
    tickets: list[dict],
    account_id: str,
    days: int = 90,
    analysis_date: str = ANALYSIS_DATE
) -> list[dict]:

    end_date = datetime.fromisoformat(
        analysis_date
    )

    cutoff = end_date - timedelta(
        days=days
    )

    account_tickets = []

    for ticket in tickets:

        # IMPORTANT:
        # Join using account_id, not company name.
        if ticket.get("account_id") != account_id:
            continue

        created_at = ticket.get("created_at")

        if not created_at:
            continue

        try:
            ticket_date = parse_datetime(
                created_at
            )
        except ValueError:
            continue

        if cutoff <= ticket_date <= end_date:
            account_tickets.append(ticket)

    account_tickets.sort(
        key=lambda t: t.get("created_at", "")
    )

    return account_tickets


def get_open_tickets(
    tickets: list[dict]
) -> list[dict]:

    closed_statuses = {
        "Resolved",
        "Closed"
    }

    return [
        ticket
        for ticket in tickets
        if ticket.get("status") not in closed_statuses
    ]


def get_p1_tickets(
    tickets: list[dict]
) -> list[dict]:

    return [
        ticket
        for ticket in tickets
        if ticket.get("urgency") == "P1"
    ]


def get_low_csat_tickets(
    tickets: list[dict]
) -> list[dict]:

    return [
        ticket
        for ticket in tickets
        if (
            ticket.get("satisfaction_score") is not None
            and ticket.get("satisfaction_score") <= 2
        )
    ]


def find_keyword_evidence(
    tickets: list[dict],
    keywords: list[str]
) -> list[dict]:

    evidence = []

    for ticket in tickets:

        subject = ticket.get(
            "subject",
            ""
        )

        body = ticket.get(
            "body",
            ""
        )

        text = f"{subject}\n{body}"

        lower_text = text.lower()

        matched_keyword = None

        for keyword in keywords:

            if keyword.lower() in lower_text:
                matched_keyword = keyword
                break

        if matched_keyword:

            evidence.append(
                {
                    "ticket_id": ticket.get(
                        "ticket_id"
                    ),
                    "keyword": matched_keyword,

                    # Keep the actual ticket text.
                    # The LLM must not invent evidence.
                    "quote": body
                }
            )

    return evidence


def build_account_snapshot(
    accounts: list[dict],
    tickets: list[dict],
    account_id: str
) -> dict:

    account = get_account(
        accounts,
        account_id
    )

    if account is None:
        raise ValueError(
            f"Account not found: {account_id}"
        )

    # ---------------------------------------------------------
    # Last 90 days of tickets
    # ---------------------------------------------------------

    account_tickets = get_account_tickets(
        tickets,
        account_id,
        days=90
    )

    # ---------------------------------------------------------
    # Ticket-derived signals
    # ---------------------------------------------------------

    open_tickets = get_open_tickets(
        account_tickets
    )

    p1_tickets = get_p1_tickets(
        account_tickets
    )

    low_csat_tickets = get_low_csat_tickets(
        account_tickets
    )

    churn_evidence = find_keyword_evidence(
        account_tickets,
        CHURN_KEYWORDS
    )

    escalation_evidence = find_keyword_evidence(
        account_tickets,
        ESCALATION_KEYWORDS
    )

    # ---------------------------------------------------------
    # Account-level signals
    # ---------------------------------------------------------

    account_escalation_notes = account.get(
        "escalation_notes",
        []
    )

    # ---------------------------------------------------------
    # Combined snapshot
    # ---------------------------------------------------------

    return {

        "analysis_date": ANALYSIS_DATE,

        "account": account,

        "account_metrics": {
            "health_status": account.get(
                "health_status"
            ),

            "usage_trend": account.get(
                "usage_trend"
            ),

            "open_tickets": account.get(
                "open_tickets"
            ),

            "p1_tickets_last_30d": account.get(
                "p1_tickets_last_30d"
            ),

            "nps_score": account.get(
                "nps_score"
            ),

            "last_login_days_ago": account.get(
                "last_login_days_ago"
            ),

            "renewal_date": account.get(
                "renewal_date"
            ),

            "arr_usd": account.get(
                "arr_usd"
            ),
            "days_until_renewal": get_days_until_renewal(
                account.get("renewal_date")
            ),
            "data_quality_warnings": check_account_consistency(
                account
            ),
        },

        "tickets_last_90_days": account_tickets,

        "ticket_metrics": {
            "total": len(account_tickets),
            "open": len(open_tickets),
            "p1": len(p1_tickets),
            "low_csat": len(low_csat_tickets)
        },

        "open_tickets_last_90_days": open_tickets,

        "p1_tickets_last_90_days": p1_tickets,

        "low_csat_tickets": low_csat_tickets,

        "ticket_churn_evidence": churn_evidence,

        "ticket_escalation_evidence": escalation_evidence,

        "account_escalation_notes": account_escalation_notes
    }

def get_days_until_renewal(
    renewal_date: str,
    analysis_date: str = ANALYSIS_DATE
) -> int:

    renewal = datetime.fromisoformat(
        renewal_date
    )

    analysis = datetime.fromisoformat(
        analysis_date
    )

    return (renewal - analysis).days