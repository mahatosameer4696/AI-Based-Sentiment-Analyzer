"""
AI-Based Sentiment Analyzer
============================
A Flask web application that uses Hugging Face Transformers
to analyze the sentiment of user-provided text.

Author: Sentiment Analyzer Project
Version: 1.0.0
"""

import os
import csv
import sqlite3
import io
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from transformers import pipeline

# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "sentiment_analyzer_secret_key_2024"

# ─────────────────────────────────────────────
# Database Configuration
# ─────────────────────────────────────────────
DATABASE = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """
    Initialize the SQLite database.
    Creates the 'analyses' table if it does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            text        TEXT    NOT NULL,
            sentiment   TEXT    NOT NULL,
            confidence  REAL    NOT NULL,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


# ─────────────────────────────────────────────
# Load Hugging Face Sentiment Pipeline
# ─────────────────────────────────────────────
print("[MODEL] Loading sentiment analysis model... (this may take a moment)")
try:
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("[MODEL] Model loaded successfully.")
except Exception as e:
    sentiment_pipeline = None
    print(f"[MODEL] Error loading model: {e}")


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def analyze_sentiment(text: str) -> dict:
    """
    Run sentiment analysis on the given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing 'sentiment' and 'confidence'.

    Raises:
        RuntimeError: If the sentiment pipeline is not loaded.
    """
    if sentiment_pipeline is None:
        raise RuntimeError("Sentiment analysis model is not available.")

    # Truncate text to 512 tokens (model limit)
    truncated_text = text[:512]

    # Get scores for BOTH labels (POSITIVE and NEGATIVE)
    raw_results = sentiment_pipeline(truncated_text, top_k=None)
    if isinstance(raw_results, list) and len(raw_results) > 0 and isinstance(raw_results[0], list):
        results = raw_results[0]
    else:
        results = raw_results
    scores = {r["label"]: r["score"] for r in results}

    pos_score = scores.get("POSITIVE", 0.5)
    neg_score = scores.get("NEGATIVE", 0.5)

    diff = abs(pos_score - neg_score)

    if diff < 0.98:
        label = "Neutral"
        confidence = round(50 + (0.98 - diff) / 0.98 * 45, 2)
    elif pos_score > neg_score:
        label = "Positive"
        confidence = round(pos_score * 100, 2)
    else:
        label = "Negative"
        confidence = round(neg_score * 100, 2)

    return {"sentiment": label, "confidence": confidence}


def save_to_db(text: str, sentiment: str, confidence: float) -> int:
    """
    Save an analysis result to the database.

    Args:
        text (str): The analyzed text.
        sentiment (str): The detected sentiment label.
        confidence (float): The confidence score (0–100).

    Returns:
        int: The ID of the newly inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO analyses (text, sentiment, confidence, created_at) VALUES (?, ?, ?, ?)",
        (text, sentiment, confidence, created_at)
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Render the home page with the analysis form."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Handle sentiment analysis form submission.
    Validates input, runs analysis, saves to DB, and returns JSON.
    """
    data = request.get_json()

    # ── Input Validation ──────────────────────
    if not data or "text" not in data:
        return jsonify({"error": "No text provided."}), 400

    text = data["text"].strip()

    if len(text) == 0:
        return jsonify({"error": "Text cannot be empty."}), 400

    if len(text) < 3:
        return jsonify({"error": "Please enter at least 3 characters."}), 400

    if len(text) > 5000:
        return jsonify({"error": "Text is too long. Maximum 5000 characters allowed."}), 400

    # ── Sentiment Analysis ────────────────────
    try:
        result = analyze_sentiment(text)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    # ── Save to Database ──────────────────────
    try:
        record_id = save_to_db(text, result["sentiment"], result["confidence"])
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({
        "id":         record_id,
        "text":       text,
        "sentiment":  result["sentiment"],
        "confidence": result["confidence"],
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route("/history", methods=["GET"])
def history():
    """
    Render the history page with all previous analyses.
    Supports optional search filtering via query parameter ?q=<term>.
    """
    search_query = request.args.get("q", "").strip()

    conn = get_db_connection()
    if search_query:
        records = conn.execute(
            """SELECT * FROM analyses
               WHERE text LIKE ? OR sentiment LIKE ?
               ORDER BY id DESC""",
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        records = conn.execute(
            "SELECT * FROM analyses ORDER BY id DESC"
        ).fetchall()
    conn.close()

    return render_template("history.html", records=records, search_query=search_query)


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id: int):
    """
    Delete a specific analysis record by ID.

    Args:
        record_id (int): The ID of the record to delete.
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM analyses WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        flash(f"Record #{record_id} deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting record: {str(e)}", "danger")

    return redirect(url_for("history"))


@app.route("/export", methods=["GET"])
def export_csv():
    """
    Export all analysis records to a CSV file for download.
    Supports optional search filtering via query parameter ?q=<term>.
    """
    search_query = request.args.get("q", "").strip()

    conn = get_db_connection()
    if search_query:
        records = conn.execute(
            """SELECT * FROM analyses
               WHERE text LIKE ? OR sentiment LIKE ?
               ORDER BY id DESC""",
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        records = conn.execute(
            "SELECT * FROM analyses ORDER BY id DESC"
        ).fetchall()
    conn.close()

    # ── Build CSV in Memory ───────────────────
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Text", "Sentiment", "Confidence (%)", "Date & Time"])

    for row in records:
        writer.writerow([row["id"], row["text"], row["sentiment"],
                         row["confidence"], row["created_at"]])

    output.seek(0)
    filename = f"sentiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/stats", methods=["GET"])
def stats():
    """Return summary statistics as JSON for the dashboard."""
    conn = get_db_connection()
    total      = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    positive   = conn.execute("SELECT COUNT(*) FROM analyses WHERE sentiment='Positive'").fetchone()[0]
    negative   = conn.execute("SELECT COUNT(*) FROM analyses WHERE sentiment='Negative'").fetchone()[0]
    neutral    = conn.execute("SELECT COUNT(*) FROM analyses WHERE sentiment='Neutral'").fetchone()[0]
    avg_conf   = conn.execute("SELECT AVG(confidence) FROM analyses").fetchone()[0]
    conn.close()

    return jsonify({
        "total":      total,
        "positive":   positive,
        "negative":   negative,
        "neutral":    neutral,
        "avg_confidence": round(avg_conf, 2) if avg_conf else 0
    })


# ─────────────────────────────────────────────
# Application Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()   # Ensure database and tables exist
    print("[APP] Starting Sentiment Analyzer at http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
