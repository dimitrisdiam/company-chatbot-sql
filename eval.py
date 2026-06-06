"""Evaluation harness for the SQL chatbot.

Runs a set of questions with known correct answers through the agent and reports
accuracy. Edit TEST_CASES to match the data in your own database, then run:

    python eval.py

The expected answer is matched loosely (case-insensitive substring), which is
enough for short factual answers. Tighten it if you need exact matching.
"""

from dotenv import load_dotenv
import os

from chatbot_app import build_agent, get_response, load_database

# (question, expected substring in the answer)
TEST_CASES = [
    ("What is the status of order 102?", "shipped"),
    ("Which products are out of stock?", "keyboard"),
    ("How many orders has customer ID 25 placed?", "3"),
    # Add the rest of your known-answer questions here.
]


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set. Add it to your .env file.")

    agent = build_agent(load_database(), api_key)

    passed = 0
    failures = []

    for question, expected in TEST_CASES:
        answer = get_response(agent, question)
        ok = expected.lower() in answer.lower()
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {question}\n        -> {answer}\n")
        if not ok:
            failures.append((question, expected, answer))

    total = len(TEST_CASES)
    print(f"Accuracy: {passed}/{total} ({passed / total:.0%})")

    if failures:
        print("\nFailures (use these in the README's results section):")
        for question, expected, answer in failures:
            print(f"  Q: {question}\n  expected ~ {expected!r}\n  got: {answer}\n")


if __name__ == "__main__":
    main()
