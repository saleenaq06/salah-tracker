import os
import sqlite3
from datetime import date

from flask import Flask, render_template, redirect, url_for, request


app = Flask(__name__)

DATABASE_PATH = os.path.join("data", "salah_tracker.db")

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

@app.route('/', methods=['GET', 'POST'])
def home():
    today = date.today().isoformat()

    if request.method == 'POST':
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
            today,
            "fajr" in request.form,
            "dhuhr" in request.form,
            "asr" in request.form,
            "maghrib" in request.form,
            "isha" in request.form,
        ))
        connection.commit()
        connection.close()

        return redirect(url_for('home', saved='true'))

    connection = get_db_connection()
    record = connection.execute("SELECT * FROM prayer_records WHERE date = ?", (today,)).fetchone()
    connection.close()

    return render_template('index.html', today=today, record=record, saved=request.args.get('saved'))

if __name__ == '__main__':
    create_database()
    app.run(debug=True)