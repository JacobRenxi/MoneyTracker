import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import main


# Function to create a user table
def create_user_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()

# Function to check user credentials
def check_user_credentials(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    return cursor.fetchone() is not None

# Function to create a new user
def create_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password) VALUES (?, ?)
    ''', (username, password))
    conn.commit()

# Function to handle user login
def user_login(conn):
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        if check_user_credentials(conn, username, password):
            print("Login successful!")
            return username
        else:
            print("Invalid username or password. Exit.")
            main.login_here()

