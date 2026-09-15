import os
import sqlite3
from datetime import date

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE_PATH = os.path.join("data", "salah_tracker.db")
PRAYERS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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


def prayer_total(record):
    return sum(record[prayer] for prayer in PRAYERS)


def get_analytics(connection):
    records = connection.execute(
        "SELECT * FROM prayer_records ORDER BY date DESC"
    ).fetchall()
    total_prayers = sum(prayer_total(record) for record in records)
    possible_prayers = len(records) * len(PRAYERS)
    completion_percentage = (
        round((total_prayers / possible_prayers) * 100) if possible_prayers else 0
    )

    current_streak = 0
    for record in records:
        if prayer_total(record) == len(PRAYERS):
            current_streak += 1
        else:
            break

    return {
        "total_prayers": total_prayers,
        "completion_percentage": completion_percentage,
        "current_streak": current_streak,
        "days_tracked": len(records),
    }


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
        "SELECT * FROM prayer_records WHERE date = ?", (selected_date,)
    ).fetchone()
    analytics = get_analytics(connection)
    connection.close()

    return render_template(
        "index.html",
        selected_date=selected_date,
        record=record,
        completed_prayers=prayer_total(record) if record else 0,
        analytics=analytics,
        saved=request.args.get("saved"),
    )


@app.route("/history")
def history():
    connection = get_db_connection()
    records = connection.execute(
        "SELECT * FROM prayer_records ORDER BY date DESC"
    ).fetchall()
    analytics = get_analytics(connection)
    connection.close()

    history_records = [
        {"date": record["date"], "completed": prayer_total(record)}
        for record in records
    ]
    return render_template(
        "history.html", records=history_records, analytics=analytics
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)

