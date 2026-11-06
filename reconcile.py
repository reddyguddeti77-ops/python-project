"""
reconcile.py

Matches merchant transactions to settlement records and classifies
each one: MATCHED / UNSETTLED / DOUBLE_SETTLED / REVERSED / AMOUNT_MISMATCH

Run it with:  python engine/reconcile.py
"""

import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paths import PROJECT_ROOT  # noqa: E402

DB_PATH = os.path.join(PROJECT_ROOT, "db", "reconciliation.db")
AMOUNT_TOLERANCE = 0.01


def run_reconciliation():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    merchant_txns = cur.execute("SELECT * FROM merchant_transactions").fetchall()
    settlements = cur.execute("SELECT * FROM npci_settlements").fetchall()

    pay_rows = [s for s in settlements if s["txn_type"] == "PAY"]
    refund_rows = [s for s in settlements if s["txn_type"] in ("REFUND", "REVERSAL")]

    pay_by_rrn = {}
    for row in pay_rows:
        pay_by_rrn.setdefault(row["rrn"], []).append(row)

    refund_by_original_rrn = {}
    for row in refund_rows:
        if row["original_rrn"]:
            refund_by_original_rrn.setdefault(row["original_rrn"], []).append(row)

    results = []

    for txn in merchant_txns:
        ref_id = txn["upi_ref_id"]
        matches = pay_by_rrn.get(ref_id, [])
        refunds = refund_by_original_rrn.get(ref_id, [])

        if refunds:
            refund_total = sum(r["settlement_amount"] for r in refunds)
            status = "REVERSED"
            notes = f"Refunded via RRN(s): {', '.join(r['rrn'] for r in refunds)}"
            matched_rrn = ", ".join(r["rrn"] for r in refunds)
            settled_amount = refund_total

        elif len(matches) == 0:
            status = "UNSETTLED"
            notes = "No matching settlement row found in NPCI file."
            matched_rrn = None
            settled_amount = None

        elif len(matches) == 1:
            settled_amount = matches[0]["settlement_amount"]
            matched_rrn = matches[0]["rrn"]
            if abs(settled_amount - txn["amount"]) <= AMOUNT_TOLERANCE:
                status = "MATCHED"
                notes = "Amount matches settlement exactly."
            else:
                status = "AMOUNT_MISMATCH"
                notes = f"Merchant amount {txn['amount']} vs settled {settled_amount}."

        else:
            status = "DOUBLE_SETTLED"
            matched_rrn = matches[0]["rrn"]
            settled_amount = sum(m["settlement_amount"] for m in matches)
            notes = f"Settled {len(matches)} times for the same transaction."

        results.append({
            "txn_id": txn["txn_id"],
            "matched_rrn": matched_rrn,
            "merchant_amount": txn["amount"],
            "settled_amount": settled_amount,
            "status": status,
            "notes": notes,
        })

    cur.execute("DELETE FROM reconciliation_results")
    cur.executemany("""
        INSERT INTO reconciliation_results
        (txn_id, matched_rrn, merchant_amount, settled_amount, status, notes)
        VALUES (:txn_id, :matched_rrn, :merchant_amount, :settled_amount, :status, :notes)
    """, results)
    conn.commit()
    conn.close()

    return results


def print_summary(results):
    from collections import Counter
    counts = Counter(r["status"] for r in results)
    print("\n--- Reconciliation Summary ---")
    for status, count in counts.items():
        print(f"{status:<16} {count}")
    print(f"{'TOTAL':<16} {len(results)}")


if __name__ == "__main__":
    results = run_reconciliation()
    print(f"Reconciled {len(results)} merchant transactions.")
    print_summary(results)
