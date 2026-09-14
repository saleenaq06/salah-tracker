import os
import sqlite3
from datetime import date

from flask import Flask, render_template, redirect, url_for, request


app = Flask(__name__)

# Define the path to the SQLite database file
DATABASE_PATH = os.path.join("data", "salah_tracker.db")

# Create a function to get a database connection
def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Create the database and the prayer_records table if they don't exist
def create_database():
    os.makedirs("data", exist_ok=True)

    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS prayer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            fajr INTEGER NOT NULL DEFAULT 0,
            dhuhr INTEGER NOT NULL DEFAULT 0,
            asr INTEGER NOT NULL DEFAULT 0,
            maghrib INTEGER NOT NULL DEFAULT 0,
            isha INTEGER NOT NULL DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():
    today = date.today().isoformat()

    if request.method == "POST":
        selected_date = request.form.get("date", today)

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO prayer_records (date, fajr, dhuhr, asr, maghrib, isha)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                fajr = excluded.fajr,
                dhuhr = excluded.dhuhr,
                asr = excluded.asr,
                maghrib = excluded.maghrib,
                isha = excluded.isha
        """, (
            selected_date,
            "fajr" in request.form,
            "dhuhr" in request.form,
            "asr" in request.form,
            "maghrib" in request.form,
            "isha" in request.form,
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("home", date=selected_date, saved="true"))

    selected_date = request.args.get("date", today)

    connection = get_db_connection()
    record = connection.execute(
        "SELECT * FROM prayer_records WHERE date = ?",
        (selected_date,)
    ).fetchone()
    connection.close()

    completed_prayers = 0
    if record:
        completed_prayers = sum(
            record[prayer]
            for prayer in ["fajr", "dhuhr", "asr", "maghrib", "isha"]
        )

    return render_template(
        "index.html",
        selected_date=selected_date,
        record=record,
        completed_prayers=completed_prayers,
        saved=request.args.get("saved")
    )


if __name__ == '__main__':
    create_database()
    app.run(debug=True)