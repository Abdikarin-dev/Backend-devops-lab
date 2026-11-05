
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)

# Store the database inside the instance folder.
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

app.config["DATABASE"] = str(INSTANCE_DIR / "feedback.db")


def init_db():
    """Create the feedback table if it does not exist."""
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                email TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    email = request.form.get("email", "").strip() or None
    message = request.form.get("message", "").strip()

    # Validate required fields.
    if not name or not country or not message:
        return render_template(
            "index.html",
            feedback_error="Please complete your name, country and advice."
        ), 400

    if email and "@" not in email:
        return render_template(
            "index.html",
            feedback_error="Please enter a valid email address."
        ), 400

    # Save feedback using parameterized SQL.
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute(
            """
            INSERT INTO feedback (name, country, email, message)
            VALUES (?, ?, ?, ?)
            """,
            (name, country, email, message)
        )

    return render_template(
        "index.html",
        feedback_success=f"Thank you, {name}! Your advice has been received."
    )


# Create the database table when the application starts.
init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

