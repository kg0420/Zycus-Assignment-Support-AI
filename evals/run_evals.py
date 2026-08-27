import json
import traceback
from pathlib import Path
from evals.evaluator import (
    is_rate_limit_error,
)
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

from src.triage import (
    triage_ticket,
)

from src.retrieval import (
    KnowledgeBaseRetriever,
)

from src.config import KB_DIR

from evals.evaluator import (
    evaluate_task1_result,
    evaluate_task2_result,
)
from evals.evaluator import calculate_summary

BASE_DIR = Path(__file__).resolve().parent


def load_cases(filename: str):

    path = BASE_DIR / filename

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def run_task1():

    print("\n")
    print("=" * 70)
    print("TASK 1 EVALUATION")
    print("=" * 70)

    cases = load_cases(
        "task1_cases.json"
    )

    retriever = KnowledgeBaseRetriever(
        KB_DIR
    )

    account_id = case["account_id"]

    results = []

    for case in cases:

        name = case["name"]

        print(
            f"\nRunning: {name}"
        )

        try:

            result = triage_ticket(
                case["ticket"],
                retriever
            )

            evaluation = evaluate_task1_result(
                result.model_dump(),
                case["expected"]
            )

            results.append(
                {
                    "name": name,
                    "score": evaluation["score"],
                    "passed": evaluation["passed"],
                    "checks": evaluation["checks"]
                }
            )

            print(
                f"Score: {evaluation['score']}"
            )

            print(
                f"Status: "
                f"{'PASS' if evaluation['passed'] else 'FAIL'}"
            )

        except Exception as exc:

            if is_rate_limit_error(exc):

                print(
                    "Status: SKIPPED "
                    "(Gemini quota/rate limit)"
                )

                results.append(
                    {
                        "name": name,
                        "account_id": account_id,
                        "status": "SKIPPED",
                        "score": None,
                        "reason": "Gemini API quota exhausted"
                    }
                )

                continue

            print(
                f"ERROR: {exc}"
            )

            results.append(
                {
                    "name": name,
                    "account_id": account_id,
                    "status": "ERROR",
                    "score": 0.0,
                    "error": str(exc)
                }
            )

    return results


def run_task2():

    print("\n")
    print("=" * 70)
    print("TASK 2 EVALUATION")
    print("=" * 70)

    cases = load_cases(
        "task2_cases.json"
    )

    accounts = load_json(
        ACCOUNTS_FILE
    )

    tickets = load_json(
        TICKETS_FILE
    )

    results = []

    for case in cases:

        name = case["name"]
        account_id = case["account_id"]

        print(
            f"\nRunning: {name}"
        )

        try:

            snapshot = build_account_snapshot(
                accounts,
                tickets,
                account_id
            )

            if case["expected"].get(
                "must_handle_error"
            ):

                results.append(
                    {
                        "name": name,
                        "account_id": account_id,
                        "score": 0.0,
                        "passed": False,
                        "error": (
                            "Expected ValueError for "
                            "missing account, but account "
                            "was found."
                        )
                    }
                )

                print(
                    "Score: 0.0"
                )

                print(
                    "Status: FAIL"
                )

                continue

            # ---------------------------------------------------------
            # Generate summary
            # ---------------------------------------------------------

            summary = summarize_account(
                snapshot
            )

            

            output = {
                "account_id": account_id,
                "summary": summary
            }

            evaluation = evaluate_task2_result(
                output,
                case["expected"]
            )

            results.append(
                {
                    "name": name,
                    "account_id": account_id,
                    "score": evaluation["score"],
                    "passed": evaluation["passed"],
                    "checks": evaluation["checks"]
                }
            )

            print(
                f"Score: {evaluation['score']}"
            )

            print(
                f"Status: "
                f"{'PASS' if evaluation['passed'] else 'FAIL'}"
            )

        except ValueError as exc:

            # ---------------------------------------------------------
            # Expected missing-account error
            # ---------------------------------------------------------

            if case["expected"].get(
                "must_handle_error"
            ):

                print(
                    "Score: 1.0"
                )

                print(
                    "Status: PASS"
                )

                results.append(
                    {
                        "name": name,
                        "account_id": account_id,
                        "score": 1.0,
                        "passed": True,
                        "checks": {
                            "missing_account_handled": True
                        }
                    }
                )

            else:

                print(
                    f"ERROR: {exc}"
                )

                results.append(
                    {
                        "name": name,
                        "account_id": account_id,
                        "score": 0.0,
                        "passed": False,
                        "error": str(exc)
                    }
                )

        except Exception as exc:

            if is_rate_limit_error(exc):

                print(
                    "Status: SKIPPED "
                    "(Gemini quota/rate limit)"
                )

                results.append(
                    {
                        "name": name,
                        "account_id": account_id,
                        "status": "SKIPPED",
                        "score": None,
                        "reason": "Gemini API quota exhausted"
                    }
                )

                continue

            print(
                f"ERROR: {exc}"
            )

            results.append(
                {
                    "name": name,
                    "account_id": account_id,
                    "status": "ERROR",
                    "score": 0.0,
                    "error": str(exc)
                }
            )

    return results


def calculate_summary(results):

    if not results:
        return {
            "total": 0,
            "passed": 0,
            "average_score": 0.0
        }

    total = len(results)

    passed = sum(
        1
        for result in results
        if result.get("passed")
    )

    average_score = sum(
        result.get("score", 0)
        for result in results
    ) / total

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "average_score": round(
            average_score,
            3
        )
    }


def main():

    task1_results = run_task1()

    task2_results = run_task2()

    task1_summary = calculate_summary(
        task1_results
    )

    task2_summary = calculate_summary(
        task2_results
    )

    report = {

        "task_1": {
            "summary": task1_summary,
            "cases": task1_results
        },

        "task_2": {
            "summary": task2_summary,
            "cases": task2_results
        }
    }

    output_path = (
        BASE_DIR.parent
        / "eval_report.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=2
        )

    print("\n")
    print("=" * 70)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 70)

    print(
        "\nTask 1:"
    )

    print(
        f"Passed: "
        f"{task1_summary['passed']}/"
        f"{task1_summary['total']}"
    )

    print(
        f"Average score: "
        f"{task1_summary['average_score']}"
    )

    print(
        "\nTask 2:"
    )

    print(
        f"Passed: "
        f"{task2_summary['passed']}/"
        f"{task2_summary['total']}"
    )

    print(
        f"Average score: "
        f"{task2_summary['average_score']}"
    )

    print(
        f"\nReport saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()