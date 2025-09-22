# Pomodoro CLI

A simple command-line Pomodoro timer built with Python.  
Start work or break sessions, automatically log them to a SQL Database, and view daily work-time statistics.

## Features
- Start a 25-minute work session or 5-minute break
- Option to set custom session lengths
- Logs sessions with timestamps in `sessions.db`
- View total work minutes for today

## Usage
```bash
python pomodoro.py work         # Start a 25 min work session
python pomodoro.py break        # Start a 5 min break
python pomodoro.py stats        # Show today's total work minutes
python pomodoro.py work --minutes 50   # Custom work time

## 🔔 New Feature: Sound Notifications
The Pomodoro CLI now plays a sound when a session ends!  

- **Windows:** A short tone is played using the built-in `winsound` module.  
- **Mac/Linux:** The terminal bell (`\a`) is triggered.  

This makes it easier to know when to take a break or get back to work, even if the terminal isn’t in focus.


## ✨ New Feature: Daily Pomodoro Goal  

You can now set a **daily goal** for completed Pomodoro sessions!  

- Start a work session with a goal:  
  ```bash
  python pomodoro.py work --goal 4
