# Pomodoro CLI

A simple command-line Pomodoro timer built with Python.  
Start work or break sessions, automatically log them to a CSV file, and view daily work-time statistics.

## Features
- Start a 25-minute work session or 5-minute break
- Option to set custom session lengths
- Logs sessions with timestamps in `sessions.csv`
- View total work minutes for today

## Usage
```bash
python pomodoro.py work         # Start a 25 min work session
python pomodoro.py break        # Start a 5 min break
python pomodoro.py stats        # Show today's total work minutes
python pomodoro.py work --minutes 50   # Custom work time
