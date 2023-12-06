import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import login


def add_expense(category, amount, description, date, cursor, conn):
    cursor.execute('''
        INSERT INTO expenses (category, amount, description, date)
        VALUES (?, ?, ?, ?)
    ''', (category, amount, description, date))
    conn.commit()

def view_expenses(cursor):
    cursor.execute('''
        SELECT * FROM expenses
    ''')
    expenses = cursor.fetchall()
    for expense in expenses:
        print(expense)

def generate_report(cursor):
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

def login_here():
    conn = sqlite3.connect('users.db')
    login.create_user_table(conn)

    print("Welcome to Expense Tracker!")
    print("1. Login")
    print("2. Register")
    choice = input("Enter your choice: ")

    if choice == '1':
        username = login.user_login(conn)
        return username
    elif choice == '2':
        new_username = input("Enter new username: ")
        new_password = input("Enter new password: ")
        try:
            login.create_user(conn, new_username, new_password)
        except sqlite3.IntegrityError:
            print("User registration unsuccessful. Username already exists")
            login_here()

        print("User registered successfully. Please login.")
        username = login.user_login(conn)
        return username
    else:
        print("Invalid choice. Exiting.")
        conn.close()

def main():    
    username = login_here()
    # After successful login, use the username for database connection
    user_db_name= f'{username}_expenses.db'

    conn = sqlite3.connect(user_db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR,
            amount FLOAT,
            description TEXT,
            date TEXT
        )
    ''')
    conn.commit()

    def lowercase_categories(categories):
        return [category.lower() for category in categories]

    '''
    Below is the categories that we can pick!
    Add more or change categories below!
    '''
    valid_categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Utilities', 'Other', 'ADD*']
    valid_categories_lower = lowercase_categories(valid_categories)

    max_budget = float(input("Enter your maximum budget: "))
    current_budget = max_budget



    while True:
        print("\nExpense Tracker")
        print("Current Budget:", current_budget)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Generate Report")
        print("4. Exit")

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
                add_expense(category, amount, description, timestamp, cursor, conn)
                print("Budget added successfully!")

            else:
                amount = float(input("Enter amount: "))
                if amount > current_budget:
                    print("Amount exceeds current budget. Please enter a smaller amount.")
                    continue

                description = input("Enter description: ")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_expense(category, amount, description, timestamp, cursor, conn)
                current_budget -= amount
                print("Expense added successfully!")

                # Display valid categories after adding an expense
                print("\nValid categories:", valid_categories)

        elif choice == '2':
            print("\nAll Expenses:")
            view_expenses(cursor)
        elif choice == '3':
            generate_report(cursor)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()
