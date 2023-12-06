import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime


conn = sqlite3.connect('expenses.db')
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
valid_categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Utilities', 'Other']
valid_categories_lower = lowercase_categories(valid_categories)


def add_expense(category, amount, description, date):
    cursor.execute('''
        INSERT INTO expenses (category, amount, description, date)
        VALUES (?, ?, ?, ?)
    ''', (category, amount, description, date))
    conn.commit()

def view_expenses():
    cursor.execute('''
        SELECT * FROM expenses
    ''')
    expenses = cursor.fetchall()
    for expense in expenses:
        print(expense)

def generate_report():
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

def main():
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

            amount = float(input("Enter amount: "))
            if amount > current_budget:
                print("Amount exceeds current budget. Please enter a smaller amount.")
                continue

            description = input("Enter description: ")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_expense(category, amount, description, timestamp)
            current_budget -= amount
            print("Expense added successfully!")

            # Display valid categories after adding an expense
            print("\nValid categories:", valid_categories)

        elif choice == '2':
            print("\nAll Expenses:")
            view_expenses()
        elif choice == '3':
            generate_report()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()
