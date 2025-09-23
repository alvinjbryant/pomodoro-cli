import sqlite3

DB_NAME = "sessions.db"

class UserManager:
    def __init__(self):
        self.current_user = None

    def signup(self, username, password):
        """Create a new user account."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print(f"User '{username}' created successfully.")
        except sqlite3.IntegrityError:
            print(f"Username '{username}' already exists.")
        finally:
            conn.close()

    def login(self, username, password):
        """Log into an existing account."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = {"id": user[0], "username": user[1]}
            print(f"Logged in as {username}")
            return True
        else:
            print("Invalid username or password.")
            return False

    def logout(self):
        """Log out of the current account."""
        if self.current_user:
            print(f"Logged out of {self.current_user['username']}")
            self.current_user = None
        else:
            print("No user currently logged in.")
