import time
import sqlite3
from datetime import datetime, date
import argparse
import os
import platform

# ----------------------------
# Database setup
# ----------------------------
DB_FILE = "sessions.db"

# Create a connection to the SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create the sessions table if it doesn’t already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each session
    date TEXT NOT NULL,                    -- Date of the session (YYYY-MM-DD)
    label TEXT NOT NULL,                   -- "Work" or "Break"
    minutes INTEGER NOT NULL               -- Duration of the session in minutes
)
''')
conn.commit()


# ----------------------------
# Function to log each session
# ----------------------------
def log_session(session_type, duration):
    """
    Logs a completed session to the SQLite database with:
    - date (YYYY-MM-DD)
    - session type (Work or Break)
    - duration in minutes
    """
    today = date.today().isoformat()
    cursor.execute(
        "INSERT INTO sessions (date, label, minutes) VALUES (?, ?, ?)",
        (today, session_type, duration)
    )
    conn.commit()


# ----------------------------
# Function to play a simple beep sound when a session ends
# ----------------------------
def beep():
    """
    Cross-platform beep notification:
    - On Windows: uses the built-in 'winsound' module to play a tone.
    - On Mac/Linux: sends the ASCII bell character (\a) to the terminal,
      which triggers the default system beep (if enabled).
    """
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)  # 1000 Hz for 500 ms
    else:
        os.system('echo -n "\a";')


# ----------------------------
# Function to run a timer
# ----------------------------
def start_timer(minutes, session_type):
    """
    Starts a countdown timer in the terminal.
    Arguments:
      minutes: how long the session lasts
      session_type: "Work" or "Break"
    """
    print(f"Starting {session_type} session for {minutes} minutes...")

    # Countdown loop (convert minutes to seconds)
    for remaining in range(minutes * 60, 0, -1):
        mins, secs = divmod(remaining, 60)  # split into MM:SS
        print(f"\r{mins:02d}:{secs:02d}", end="")
        time.sleep(1)

    print(f"\n{session_type} session finished!")
    beep()  # Play sound notification when session ends

    # Log session in the database
    log_session(session_type, minutes)


# ----------------------------
# Function to show today's stats
# ----------------------------
def show_stats():
    """
    Reads the SQLite database and sums up all 'Work' sessions
    that happened today. Displays total minutes worked.
    """
    today = date.today().isoformat()
    cursor.execute(
        "SELECT SUM(minutes) FROM sessions WHERE date = ? AND label = 'Work'",
        (today,)
    )
    result = cursor.fetchone()[0]

    if result:
        print(f"Total work time today: {result} minutes")
    else:
        print("No sessions logged yet today.")


# ----------------------------
# Main entry point
# ----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pomodoro CLI Tool")

    parser.add_argument(
        "command",
        choices=["work", "break", "stats"],
        help="Start work, break, or show stats"
    )
    parser.add_argument("--minutes", type=int, default=None, help="Custom minutes")

    args = parser.parse_args()

    if args.command == "work":
        start_timer(args.minutes or 25, "Work")  # default = 25 min
    elif args.command == "break":
        start_timer(args.minutes or 5, "Break")  # default = 5 min
    elif args.command == "stats":
        show_stats()
