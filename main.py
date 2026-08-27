import json

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
)


def main():

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    accounts = load_json(
        ACCOUNTS_FILE
    )

    tickets = load_json(
        TICKETS_FILE
    )

    print(
        "\nSupport AI - Account Health Analysis"
    )

    print("=" * 60)

    print(
        f"Total accounts : {len(accounts)}"
    )

    print(
        f"Total tickets  : {len(tickets)}"
    )

    # ---------------------------------------------------------
    # Account selection
    # ---------------------------------------------------------

    account_id = accounts[0]["account_id"]

    print(
        f"\nAnalyzing account: {account_id}"
    )

    # ---------------------------------------------------------
    # Build deterministic snapshot
    # ---------------------------------------------------------

    snapshot = build_account_snapshot(
        accounts,
        tickets,
        account_id
    )

    account = snapshot["account"]

    print("\nAccount")
    print("-" * 60)

    print(
        f"Company       : "
        f"{account.get('company')}"
    )

    print(
        f"Health        : "
        f"{account.get('health_status')}"
    )

    print(
        f"Usage trend   : "
        f"{account.get('usage_trend')}"
    )

    print(
        f"Open tickets  : "
        f"{account.get('open_tickets')}"
    )

    print(
        f"Renewal date  : "
        f"{account.get('renewal_date')}"
    )

    # ---------------------------------------------------------
    # 90-day ticket metrics
    # ---------------------------------------------------------

    metrics = snapshot[
        "ticket_metrics"
    ]

    print("\n90-Day Ticket Metrics")
    print("-" * 60)

    print(
        f"Total tickets : {metrics['total']}"
    )

    print(
        f"Open tickets  : {metrics['open']}"
    )

    print(
        f"P1 tickets    : {metrics['p1']}"
    )

    print(
        f"Low CSAT      : {metrics['low_csat']}"
    )

    # ---------------------------------------------------------
    # Account escalation notes
    # ---------------------------------------------------------

    print("\nAccount Escalation Notes")
    print("-" * 60)

    for note in snapshot[
        "account_escalation_notes"
    ]:

        print(
            f"- {note}"
        )

    # ---------------------------------------------------------
    # Generate AI summary
    # ---------------------------------------------------------

    print("\nGenerating QBR Summary...")
    print("-" * 60)

    summary = summarize_account(
        snapshot
    )

    # ---------------------------------------------------------
    # Display Executive Summary
    # ---------------------------------------------------------

    print("\nEXECUTIVE SUMMARY")
    print("=" * 60)

    print(
        summary.get(
            "executive_summary",
            "No summary generated."
        )
    )

    # ---------------------------------------------------------
    # Display Risks
    # ---------------------------------------------------------

    print("\nOPEN RISKS")
    print("=" * 60)

    risks = summary.get(
        "open_risks",
        []
    )

    if not risks:

        print(
            "No evidence-backed risks identified."
        )

    else:

        for index, risk in enumerate(
            risks,
            start=1
        ):

            print(
                f"\n{index}. "
                f"{risk.get('risk_type')} "
                f"[{risk.get('severity')}]"
            )

            print(
                f"Description: "
                f"{risk.get('description')}"
            )

            print(
                f"Evidence source: "
                f"{risk.get('evidence_source')}"
            )

            if risk.get("ticket_id"):

                print(
                    f"Ticket ID: "
                    f"{risk.get('ticket_id')}"
                )

            if risk.get("quote"):

                print(
                    f"Quote: "
                    f"{risk.get('quote')}"
                )

    # ---------------------------------------------------------
    # Display TAM talking points
    # ---------------------------------------------------------

    print("\nTAM TALKING POINTS")
    print("=" * 60)

    talking_points = summary.get(
        "tam_talking_points",
        []
    )

    for index, point in enumerate(
        talking_points,
        start=1
    ):

        print(
            f"{index}. {point}"
        )

    # ---------------------------------------------------------
    # Save result
    # ---------------------------------------------------------

    output = {
        "account_id": account_id,
        "summary": summary
    }

    with open(
        "account_health_output.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        "\nSaved: account_health_output.json"
    )


if __name__ == "__main__":
    main()