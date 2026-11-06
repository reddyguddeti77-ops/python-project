import os
import sys
import sqlite3
import threading
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paths import PROJECT_ROOT, BUNDLE_ROOT  # noqa: E402
from db.load_data import main as load_data_main  # noqa: E402
from engine.reconcile import run_reconciliation  # noqa: E402

DB_PATH = os.path.join(PROJECT_ROOT, "db", "reconciliation.db")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

STATIC_DIR = os.path.join(BUNDLE_ROOT, "frontend", "static")
TEMPLATE_DIR = os.path.join(BUNDLE_ROOT, "frontend", "templates")

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)


@app.route("/")
def home():
    return send_from_directory(TEMPLATE_DIR, "index.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route("/api/results")
def api_results():
    if not os.path.exists(DB_PATH):
        return jsonify({"rows": [], "summary": {}})

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM reconciliation_results")]
    conn.close()

    summary = {}
    for row in rows:
        summary[row["status"]] = summary.get(row["status"], 0) + 1

    return jsonify({"rows": rows, "summary": summary})


@app.route("/api/upload", methods=["POST"])
def api_upload():
    merchant_file = request.files.get("merchant_file")
    settlement_file = request.files.get("settlement_file")

    if not merchant_file or not settlement_file:
        return jsonify({"error": "Both files are required."}), 400

    merchant_file.save(os.path.join(DATA_DIR, "merchant_transactions.csv"))
    settlement_file.save(os.path.join(DATA_DIR, "npci_settlement.csv"))

    load_data_main()
    run_reconciliation()

    return jsonify({"message": "Reconciliation complete."})


def open_browser():
    url = "http://localhost:5000"
    try:
        if sys.platform == "win32":
   
            os.startfile(url)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"\nCould not open the browser automatically ({e}).")
        print(f"Please open this link yourself: {url}")


def main():
    print("Starting server at http://localhost:5000")
    print("Your browser should open automatically. If not, open that link yourself.")
    print("Close this window (or press Ctrl+C) to stop the server.")
    threading.Timer(1.25, open_browser).start()
    app.run(debug=False, use_reloader=False, port=5000)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        print("\n" + "=" * 50)
        print("SOMETHING WENT WRONG - here is the full error:")
        print("=" * 50)
        traceback.print_exc()
        print("=" * 50)
    finally:
        if getattr(sys, "frozen", False):
            input("\nPress Enter to close this window...")