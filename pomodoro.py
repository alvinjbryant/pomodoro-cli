import time
import sqlite3
import argparse
import os
import platform
from datetime import datetime, date
from user_manager import UserManager

DB_NAME = "sessions.db"
user_manager = UserManager()

# ----------------------------
# Initialize database tables
# ----------------------------
def init_db():
    """
    Create sessions table if it doesn't exist.
    Each session is linked to a user via user_id.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# ----------------------------
# Save a session
# ----------------------------
def save_session(user_id, start_time, end_time, duration, session_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (user_id, start_time, end_time, duration, type) VALUES (?, ?, ?, ?, ?)",
        (user_id, start_time, end_time, duration, session_type),
    )
    conn.commit()
    conn.close()

# ----------------------------
# Beep sound when session ends
# ----------------------------
def beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    else:
        os.system('echo -n "\a";')

# ----------------------------
# Start a timer
# ----------------------------
def start_timer(user_id, minutes, session_type, goal=None):
    print(f"Starting {session_type} session for {minutes} minutes...")
    start_time = datetime.now()

    for remaining in range(minutes * 60, 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"\r{mins:02d}:{secs:02d}", end="")
        time.sleep(1)

    print(f"\n{session_type} session finished!")
    beep()

    end_time = datetime.now()
    duration = (end_time - start_time).seconds // 60
    save_session(user_id, start_time.isoformat(), end_time.isoformat(), duration, session_type)

    # Track goal progress if Work session
    if session_type == "Work" and goal:
        show_goal_progress(user_id, goal)

# ----------------------------
# Show daily stats
# ----------------------------
def show_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    today = date.today().isoformat()

    cur.execute(
        "SELECT SUM(duration) FROM sessions WHERE user_id=? AND type='Work' AND start_time LIKE ?",
        (user_id, today + "%"),
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    print(f"Total work time today: {total} minutes")

# ----------------------------
# Show goal progress
# ----------------------------
def show_goal_progress(user_id, goal):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    today = date.today().isoformat()

    cur.execute(
        "SELECT COUNT(*) FROM sessions WHERE user_id=? AND type='Work' AND start_time LIKE ?",
        (user_id, today + "%"),
    )
    count = cur.fetchone()[0]
    conn.close()

    print(f"Progress: {count}/{goal} Pomodoros completed today")
    if count >= goal:
        print("Congratulations! You’ve reached your daily goal!")

# ----------------------------
# CLI Menu (interactive)
# ----------------------------
def interactive_menu():
    while True:
        print("\n=== Pomodoro CLI ===")
        print("1. Sign up")
        print("2. Log in")
        print("3. Start a Pomodoro session")
        print("4. View stats")
        print("5. Log out")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter new username: ")
            password = input("Enter new password: ")
            user_manager.signup(username, password)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_manager.login(username, password)

        elif choice == "3":
            if not user_manager.current_user:
                print("You must log in first.")
            else:
                minutes = int(input("Work session length (default 25): ") or 25)
                goal = input("Daily goal (press enter to skip): ")
                start_timer(user_manager.current_user["id"], minutes, "Work", goal=int(goal) if goal else None)

        elif choice == "4":
            if not user_manager.current_user:
                print("You must log in first.")
            else:
                show_stats(user_manager.current_user["id"])

        elif choice == "5":
            user_manager.logout()

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

# ----------------------------
# Main Entry Point
# ----------------------------
if __name__ == "__main__":
    init_db()

    parser = argparse.ArgumentParser(description="Pomodoro CLI Tool")
    parser.add_argument("--cli", action="store_true", help="Run in interactive menu mode")
    parser.add_argument("--work", type=int, help="Start a work session with custom minutes")
    parser.add_argument("--break", type=int, dest="break_minutes", help="Start a break with custom minutes")
    parser.add_argument("--goal", type=int, help="Set a daily Pomodoro goal (used with --work)")
    parser.add_argument("--user", type=str, help="Username for login (required if not using --cli)")
    parser.add_argument("--password", type=str, help="Password for login (required if not using --cli)")
    args = parser.parse_args()

    if args.cli:
        # Interactive menu handles login/signup
        interactive_menu()

    elif args.work or args.break_minutes:
        # Attempt login if not already logged in
        if not user_manager.current_user:
            if args.user and args.password:
                logged_in = user_manager.login(args.user, args.password)
                if not logged_in:
                    print("Login failed. Exiting.")
                    exit(1)
            else:
                print("You must provide --user and --password, or use --cli for interactive login.")
                exit(1)

        # Start work session if specified
        if args.work:
            start_timer(user_manager.current_user["id"], args.work, "Work", goal=args.goal)

        # Start break session if specified
        if args.break_minutes:
            start_timer(user_manager.current_user["id"], args.break_minutes, "Break")

    else:
        parser.print_help()
