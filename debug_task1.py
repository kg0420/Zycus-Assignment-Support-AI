import json

from src.config import KB_DIR
from src.retrieval import KnowledgeBaseRetriever
from src.triage import triage_ticket


CASES = [
    "critical_production_outage",
    "billing_question",
    "ambiguous_authentication_issue",
]


def main():

    with open(
        "evals/task1_cases.json",
        "r",
        encoding="utf-8"
    ) as f:
        cases = json.load(f)

    retriever = KnowledgeBaseRetriever(KB_DIR)

    for case in cases:

        if case["name"] not in CASES:
            continue

        print("\n")
        print("=" * 70)
        print(case["name"])
        print("=" * 70)

        print("\nEXPECTED:")
        print(
            json.dumps(
                case["expected"],
                indent=2
            )
        )

        result = triage_ticket(
            case["ticket"],
            retriever
        )

        print("\nACTUAL:")
        print(
            json.dumps(
                result.model_dump(),
                indent=2
            )
        )


if __name__ == "__main__":
    main()