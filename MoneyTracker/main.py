import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import login
import csv

def add_expense(category, amount, description, date, user_db_name):

    conn_expenses = sqlite3.connect(user_db_name)
    cursor = conn_expenses.cursor()
    try:
        cursor.execute('''
            INSERT INTO expenses (category, amount, description, date)
            VALUES (?, ?, ?, ?)
        ''', (category, amount, description, date))
        conn_expenses.commit()
        conn_expenses.close()
    except sqlite3.Error as e:
        print("Error adding expense:", e)

def user_exp_database(username):
    # After successful login, use the username for database connection
    user_db_name= f'{username}_expenses.db'

    conn_expenses = sqlite3.connect(user_db_name)
    cursor = conn_expenses.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR,
            amount FLOAT,
            description TEXT,
            date TEXT
        )
    ''')
    conn_expenses.commit()
    conn_expenses.close()
    return cursor, user_db_name

def view_expenses(cursor, user_db_name):
    conn_expenses = sqlite3.connect(user_db_name)
    cursor = conn_expenses.cursor()
    try:
        cursor.execute('''
            SELECT * FROM expenses
        ''')
        expenses = cursor.fetchall()
        if expenses:
            for expense in expenses:
                print(expense)
        else:
            print("No expenses found.")

        conn_expenses.commit()
        conn_expenses.close()
    except sqlite3.Error as e:
        print("Error retrieving expenses:", e)

def generate_report(cursor, user_db_name):
    conn_expenses = sqlite3.connect(user_db_name)
    cursor = conn_expenses.cursor()
    cursor.execute('''
        SELECT category, SUM(amount) as total_amount
        FROM expenses
        GROUP BY category
    ''')
    categories = []
    amounts = []
    for row in cursor.fetchall():
        categories.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Expense Distribution by Category')
    plt.axis('equal')
    plt.show()
    conn_expenses.commit()
    conn_expenses.close()

def login_here():
    conn = sqlite3.connect('users.db')
    login.create_user_table(conn)
    login.create_user_budget_table(conn)

    print("Welcome to Expense Tracker!")
    print("1. Login")
    print("2. Register")
    choice = input("Enter your choice: ")

    if choice == '1':
        username = login.user_login(conn)
        return username, conn
    elif choice == '2':
        new_username = input("Enter new username: ")
        new_password = input("Enter new password: ")
        try:
            username = login.create_user(conn, new_username, new_password)
            print(f"Welcome {username}")
        except sqlite3.IntegrityError:
            print("User registration unsuccessful. Username already exists")

        return username, conn
    else:
        print("Invalid choice. Exiting.")
        conn.close()

def lowercase_categories(categories):
    return [category.lower() for category in categories]

def export_csv(user_db_name):
    conn_expenses = sqlite3.connect(user_db_name)
    cursor = conn_expenses.cursor()
    cursor.execute('''
        SELECT *
        FROM expenses
    ''')
    with open(user_db_name[:-3]+".csv", 'w', newline='') as f:
        writer = csv.writer(f)
        fieldnames = ['id', 'category', 'amount', 'description', 'date']
        writer.writerow(fieldnames)
        writer.writerows(cursor)
    cursor.close()


def main():    
    username, conn = login_here()
    # Retrieve user's budget information
    user_budget_info = login.get_user_budget(conn, username)
    if user_budget_info:
        max_budget, current_budget = user_budget_info
    else:
        max_budget = float(input("Enter your maximum budget: "))
        current_budget = max_budget
        login.save_user_budget(conn, username, max_budget, current_budget)
    
    cursor, user_db_name = user_exp_database(username)
    
    '''
    Below is the categories that we can pick!
    Add more or change categories below!
    '''
    valid_categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Utilities', 'Other', 'ADD*']
    valid_categories_lower = lowercase_categories(valid_categories)

    while True:
        print("\nExpense Tracker")
        print("Current Budget:", current_budget)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Generate Report")
        print("4. Export Expense csv")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            # Display valid categories before prompting for category input
            print("Valid categories:", valid_categories)
            category = input("Enter category: ")
            category = category.lower()

            while category not in valid_categories_lower:
                print("Invalid category. Valid categories are:", valid_categories)
                category = input("Enter a valid category: ")

            if category == 'add*':
                amount = float(input("Enter amount adding to current budget: "))
                current_budget += amount
                print("Budget updated successfully!")
                description = input("Enter description: ")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_expense(category, amount, description, timestamp, user_db_name)
                print("Budget added successfully!")

            else:
                amount = float(input("Enter amount: "))
                if amount > current_budget:
                    print("Amount exceeds current budget. Please enter a smaller amount.")
                    continue

                description = input("Enter description: ")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_expense(category, amount, description, timestamp, user_db_name)
                current_budget -= amount
                print("Expense added successfully!")

                # Display valid categories after adding an expense
                print("\nValid categories:", valid_categories)

        elif choice == '2':
            print("\nAll Expenses:")
            view_expenses(cursor, user_db_name)
        elif choice == '3':
            generate_report(cursor, user_db_name)
        elif choice == '4':
            export_csv(user_db_name)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

        login.save_user_budget(conn, username, max_budget, current_budget)

    conn.close()

if __name__ == "__main__":
    main()
