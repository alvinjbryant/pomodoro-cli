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

def init_db():
    """
    Initialize the database and create the sessions table if it doesn't exist.
    Columns:
    - id: unique row identifier
    - timestamp: ISO string when the session was completed
    - session_type: "Work" or "Break"
    - duration: session length in minutes
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_type TEXT NOT NULL,
            duration INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ----------------------------
# Function to log each session
# ----------------------------
def log_session(session_type, duration):
    """
    Logs a completed session into the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (timestamp, session_type, duration) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), session_type, duration),
    )
    conn.commit()
    conn.close()


# ----------------------------
# Function to play a simple beep sound when a session ends
# ----------------------------
def beep():
    """
    Cross-platform beep notification.
    - Windows: uses winsound.Beep
    - Mac/Linux: uses ASCII bell character
    """
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    else:
        os.system('echo -n "\a";')


# ----------------------------
# Function to run a timer
# ----------------------------
def start_timer(minutes, session_type, goal=None):
    """
    Starts a countdown timer, logs the session, and checks progress.
    """
    print(f"Starting {session_type} session for {minutes} minutes...")

    for remaining in range(minutes * 60, 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"\r{mins:02d}:{secs:02d}", end="")
        time.sleep(1)

    print(f"\n{session_type} session finished!")
    beep()

    log_session(session_type, minutes)

    # If it's a Work session, show goal progress
    if session_type == "Work" and goal:
        show_goal_progress(goal)


# ----------------------------
# Function to show today's work stats
# ----------------------------
def show_stats():
    """
    Reads the database and sums up all 'Work' sessions for today.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    today = date.today().isoformat()

    cur.execute(
        "SELECT SUM(duration) FROM sessions WHERE session_type = 'Work' AND timestamp LIKE ?",
        (today + "%",),
    )
    total = cur.fetchone()[0] or 0
    conn.close()

    print(f"Total work time today: {total} minutes")


# ----------------------------
# Function to show progress toward daily goal
# ----------------------------
def show_goal_progress(goal):
    """
    Shows how many work sessions have been completed today vs. the goal.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    today = date.today().isoformat()

    cur.execute(
        "SELECT COUNT(*) FROM sessions WHERE session_type = 'Work' AND timestamp LIKE ?",
        (today + "%",),
    )
    count = cur.fetchone()[0]
    conn.close()

    print(f"Progress: {count}/{goal} Pomodoros completed today")
    if count >= goal:
        print("🎉 Congratulations! You’ve reached your daily goal! 🎉")


# ----------------------------
# Main entry point
# ----------------------------
if __name__ == "__main__":
    init_db()

    parser = argparse.ArgumentParser(description="Pomodoro CLI Tool")
    parser.add_argument("command", choices=["work", "break", "stats"], help="Start work, break, or show stats")
    parser.add_argument("--minutes", type=int, default=None, help="Custom minutes")
    parser.add_argument("--goal", type=int, help="Set a daily Pomodoro goal (e.g., 4)")

    args = parser.parse_args()

    if args.command == "work":
        start_timer(args.minutes or 25, "Work", goal=args.goal)
    elif args.command == "break":
        start_timer(args.minutes or 5, "Break")
    elif args.command == "stats":
        show_stats()
