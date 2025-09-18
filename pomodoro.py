import time
import csv
from datetime import datetime, date
import argparse
import os
import platform
# ----------------------------
# File where we store session logs
# ----------------------------
LOG_FILE = "sessions.csv"


# ----------------------------
# Function to log each session
# ----------------------------
def log_session(session_type, duration):
    """
    Logs a completed session to the CSV file with:
    - timestamp (when it finished)
    - session type (Work or Break)
    - duration in minutes
    """
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), session_type, duration])

# Function to play a simple beep sound when a session ends
def beep():
    """
    Cross-platform beep notification:
    - On Windows: uses the built-in 'winsound' module to play a tone.
    - On Mac/Linux: sends the ASCII bell character (\a) to the terminal,
      which triggers the default system beep (if enabled).
    """
    if platform.system() == "Windows":
        # Windows-specific sound
        import winsound
        # Beep at 1000 Hz for 500 milliseconds
        winsound.Beep(1000, 500)
    else:
        # On Mac/Linux, '\a' is the bell character.
        # 'echo -n' prevents adding a newline after it.
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
        mins, secs = divmod(remaining, 60)  # split total seconds into minutes:seconds
        # Print time in MM:SS format, overwrite same line
        print(f"\r{mins:02d}:{secs:02d}", end="")
        time.sleep(1)  # wait 1 second before updating

    print(f"\n{session_type} session finished!")
    beep()  # Play sound notification when session ends

    # Log session in CSV file after it's completed
    log_session(session_type, minutes)


# ----------------------------
# Function to show today's stats
# ----------------------------
def show_stats():
    """
    Reads the CSV log file and sums up all 'Work' sessions
    that happened today. Displays total minutes worked.
    """
    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.reader(f)
            today = date.today().isoformat()
            total = 0

            for row in reader:
                ts, session_type, duration = row
                # Count only today's "Work" sessions
                if ts.startswith(today) and session_type == "Work":
                    total += int(duration)

            print(f"Total work time today: {total} minutes")

    except FileNotFoundError:
        # Handle case where log file does not exist yet
        print("No sessions logged yet.")


# ----------------------------
# Main entry point
# ----------------------------
if __name__ == "__main__":
    # argparse lets us handle commands from the terminal
    parser = argparse.ArgumentParser(description="Pomodoro CLI Tool")

    # User chooses between starting a work session, break, or showing stats
    parser.add_argument(
        "command",
        choices=["work", "break", "stats"],
        help="Start work, break, or show stats"
    )

    # Optional flag for custom minutes (e.g., --minutes 50)
    parser.add_argument("--minutes", type=int, default=None, help="Custom minutes")

    args = parser.parse_args()

    # Match command to function
    if args.command == "work":
        start_timer(args.minutes or 25, "Work")  # default = 25 min
    elif args.command == "break":
        start_timer(args.minutes or 5, "Break")  # default = 5 min
    elif args.command == "stats":
        show_stats()
