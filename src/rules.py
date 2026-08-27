from src.models import TriageResult


ALLOWED_CATEGORIES = {
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
}


TEAM_MAPPING = {
    "Feature Request": "Product Team",
    "How-To": "Technical Support",
    "Performance": "Technical Support",
    "Billing": "Billing Support",
    "Integration": "Technical Support",
    "Onboarding": "Customer Success",
    "Data Loss": "Incident Response",
}


def validate_triage(result: TriageResult) -> TriageResult:
    """
    Validate and normalize the LLM's triage result.
    """

    # ---------------------------------------------------------
    # Validate category
    # ---------------------------------------------------------

    if result.category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Invalid category: {result.category}. "
            f"Expected one of: {sorted(ALLOWED_CATEGORIES)}"
        )

    # ---------------------------------------------------------
    # Validate urgency
    # ---------------------------------------------------------

    if result.urgency not in {"P1", "P2", "P3", "P4"}:
        raise ValueError(
            f"Invalid urgency: {result.urgency}"
        )

    # ---------------------------------------------------------
    # Deterministic team assignment
    # ---------------------------------------------------------

    result.recommended_team = TEAM_MAPPING[
        result.category
    ]

    return result

def infer_category_from_ticket(
    ticket: dict
) -> str | None:

    subject = ticket.get(
        "subject",
        ""
    ).lower()

    body = ticket.get(
        "body",
        ""
    ).lower()

    text = f"{subject}\n{body}"

    # ---------------------------------------------------------
    # Billing
    # ---------------------------------------------------------

    billing_terms = [
        "invoice",
        "charged",
        "billing",
        "subscription",
        "payment",
        "credit"
    ]

    if any(
        term in text
        for term in billing_terms
    ):
        return "Billing"

    # ---------------------------------------------------------
    # SSO / integration
    # ---------------------------------------------------------

    integration_terms = [
        "sso",
        "saml",
        "identity provider",
        "idp",
        "integration",
        "connector",
        "api connection",
        "authentication configuration"
    ]

    if any(
        term in text
        for term in integration_terms
    ):

        # Don't classify pure "how do I..." questions
        # as integration automatically.

        how_to_patterns = [
            "how do i",
            "how can i",
            "how to",
            "could you explain",
            "please explain"
        ]

        if not any(
            pattern in text
            for pattern in how_to_patterns
        ):
            return "Integration"

    return None

def infer_urgency_from_ticket(
    ticket: dict
) -> str | None:

    subject = ticket.get(
        "subject",
        ""
    ).lower()

    body = ticket.get(
        "body",
        ""
    ).lower()

    text = f"{subject}\n{body}"

    # ---------------------------------------------------------
    # Critical
    # ---------------------------------------------------------

    critical_signals = [
        "production is completely unavailable",
        "production outage",
        "business operations are blocked",
        "business continuity at risk",
        "complete outage",
        "all users unable to",
        "critical data loss"
    ]

    if any(
        signal in text
        for signal in critical_signals
    ):
        return "P1"

    # ---------------------------------------------------------
    # Billing / informational
    # ---------------------------------------------------------

    billing_signals = [
        "invoice",
        "charged",
        "billing question",
        "billing discrepancy"
    ]

    if any(
        signal in text
        for signal in billing_signals
    ):

        return "P4"

    # ---------------------------------------------------------
    # Explicit How-To
    # ---------------------------------------------------------

    how_to_signals = [
        "how do i",
        "how can i",
        "how to configure",
        "could you explain"
    ]

    if any(
        signal in text
        for signal in how_to_signals
    ):

        return "P4"

    return None