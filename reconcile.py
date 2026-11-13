
#!/usr/bin/env python3
"""Reconcile payment events using the latest attempt per transaction."""

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
latest_payments = {}

with (BASE_DIR / "payments.jsonl").open(encoding="utf-8") as file:
    for line in file:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        previous = latest_payments.get(txn_id)

        if previous is None or event["ts"] >= previous["ts"]:
            latest_payments[txn_id] = event

total = Decimal("0")
count = 0

for event in latest_payments.values():
    if event["status"] == "success":
        amount = Decimal(str(event["amount"]).replace(",", ""))
        total += amount
        count += 1

with (BASE_DIR / "expected.txt").open() as file:
    expected = int(file.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
else:
    code_amount = total.quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{code_amount}")
