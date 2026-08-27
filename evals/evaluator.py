from typing import Any


def value_matches(
    actual: Any,
    expected: Any
) -> bool:
    """
    Supports exact values and a list of acceptable values.
    """

    if isinstance(expected, list):
        return actual in expected

    return actual == expected


def evaluate_task1_result(
    result: dict,
    expected: dict
) -> dict:
    """
    Evaluate a Task 1 triage result.

    Each criterion contributes equally to the score.
    """

    checks = {}

    # ---------------------------------------------------------
    # Urgency
    # ---------------------------------------------------------

    if "urgency" in expected:

        checks["urgency"] = value_matches(
            result.get("urgency"),
            expected["urgency"]
        )

    # ---------------------------------------------------------
    # Category
    # ---------------------------------------------------------

    if "category" in expected:

        checks["category"] = value_matches(
            result.get("category"),
            expected["category"]
        )

    # ---------------------------------------------------------
    # Product area
    # ---------------------------------------------------------

    if "product_area" in expected:

        checks["product_area"] = value_matches(
            result.get("product_area"),
            expected["product_area"]
        )

    # ---------------------------------------------------------
    # Score
    # ---------------------------------------------------------

    if not checks:

        score = 0.0

    else:

        score = sum(
            1 for passed in checks.values()
            if passed
        ) / len(checks)

    return {
        "passed": score == 1.0,
        "score": round(score, 3),
        "checks": checks
    }


def evaluate_task2_result(
    result: dict,
    expected: dict
) -> dict:
    """
    Evaluate Task 2 QBR summary.
    """

    checks = {}

    summary = result.get(
        "summary",
        result
    )

    # ---------------------------------------------------------
    # Executive summary exists
    # ---------------------------------------------------------

    executive_summary = summary.get(
        "executive_summary"
    )

    checks["executive_summary_exists"] = bool(
        executive_summary
        and isinstance(
            executive_summary,
            str
        )
    )

    # ---------------------------------------------------------
    # Open risks exists
    # ---------------------------------------------------------

    risks = summary.get(
        "open_risks",
        []
    )

    checks["open_risks_is_list"] = isinstance(
        risks,
        list
    )

    # ---------------------------------------------------------
    # TAM talking points
    # ---------------------------------------------------------

    talking_points = summary.get(
        "tam_talking_points",
        []
    )

    checks["talking_points_is_list"] = isinstance(
        talking_points,
        list
    )

    # ---------------------------------------------------------
    # Churn risk
    # ---------------------------------------------------------

    if expected.get(
        "must_identify_churn_risk"
    ):

        checks[
            "churn_risk_identified"
        ] = contains_risk_type(
            risks,
            "churn"
        )

    # ---------------------------------------------------------
    # Escalation signal
    # ---------------------------------------------------------

    if expected.get(
        "must_identify_escalation_signal"
    ):

        checks[
            "escalation_identified"
        ] = contains_risk_type(
            risks,
            "escalation"
        )

    # ---------------------------------------------------------
    # Account escalation notes
    # ---------------------------------------------------------

    if expected.get(
        "must_identify_account_escalation_notes"
    ):

        checks[
            "account_escalation_identified"
        ] = contains_text(
            summary,
            [
                "3 consecutive P1",
                "P1 tickets",
                "escalation"
            ]
        )

    # ---------------------------------------------------------
    # Prevent fabricated ticket quotes
    # ---------------------------------------------------------

    if expected.get(
        "must_not_invent_ticket_quote"
    ):

        checks[
            "no_invalid_ticket_quote"
        ] = validate_ticket_evidence(
            risks
        )

    # ---------------------------------------------------------
    # Score
    # ---------------------------------------------------------

    if not checks:

        score = 0.0

    else:

        score = sum(
            1 for passed in checks.values()
            if passed
        ) / len(checks)

    return {
        "passed": score == 1.0,
        "score": round(score, 3),
        "checks": checks
    }


def contains_risk_type(
    risks: list,
    risk_type: str
) -> bool:

    target = risk_type.lower()

    for risk in risks:

        if not isinstance(risk, dict):
            continue

        current = str(
            risk.get(
                "risk_type",
                ""
            )
        ).lower()

        if target in current:
            return True

    return False


def contains_text(
    obj,
    search_terms: list[str]
) -> bool:

    text = str(obj).lower()

    return any(
        term.lower() in text
        for term in search_terms
    )


def validate_ticket_evidence(
    risks: list
) -> bool:
    """
    Every ticket-based risk must contain
    a ticket ID and a quote.
    """

    for risk in risks:

        if not isinstance(risk, dict):
            continue

        if risk.get(
            "evidence_source"
        ) == "ticket":

            if not risk.get(
                "ticket_id"
            ):
                return False

            if not risk.get(
                "quote"
            ):
                return False

    return True