# vulnerable_python_sql_injection_large.py
import sqlite3
import sys


class UserAuth:
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_name)
            return conn
        except Exception as e:
            print("Connection error:", e)
            sys.exit(1)

    def login(self, username, password):
        conn = self.connect()
        cursor = conn.cursor()

       
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("[DEBUG] Executing:", query)

        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            print("Query failed:", e)
            result = []

        conn.close()
        return result

    def print_users(self):
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id, username FROM users")
            users = cursor.fetchall()
            for u in users:
                print("User:", u)
        except Exception as e:
            print("Error:", e)

        conn.close()


def main():
    db = UserAuth("users.db")

    while True:
        print("\n1. Login")
        print("2. List users")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            user = input("Username: ")
            pwd = input("Password: ")

            result = db.login(user, pwd)

            if result:
                print("Login success:", result)
            else:
                print("Invalid credentials")

        elif choice == "2":
            db.print_users()

        elif choice == "3":
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
