# SalahTracker

A private, local web app for recording the five daily prayers and reflecting on consistency over time.

## Features

- Record Fajr, Dhuhr, Asr, Maghrib, and Isha for any selected date.
- Update a saved date without creating duplicate records.
- See a daily completion score and progress bar.
- Review every saved date in a history page.
- View total prayers logged, overall completion percentage, and a current full-day streak.

## Built with

- Python
- Flask
- SQLite
- HTML and CSS

## Run locally

1. Create and activate a virtual environment.
2. Install the project packages:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

The app creates `data/salah_tracker.db` automatically. This local database is intentionally ignored by Git so personal prayer records are never committed.
