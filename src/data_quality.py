def check_account_consistency(
    account: dict
) -> list[str]:

    warnings = []

    p1_count = account.get(
        "p1_tickets_last_30d"
    )

    notes = account.get(
        "escalation_notes",
        []
    )

    has_three_p1_note = any(
        "3 consecutive P1" in note
        for note in notes
    )

    if (
        has_three_p1_note
        and p1_count == 0
    ):
        warnings.append(
            "Account escalation notes mention "
            "3 consecutive P1 tickets in the last "
            "30 days, but p1_tickets_last_30d is 0."
        )

    return warnings