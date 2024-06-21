import json
from funcs import print_transactions, print_categories, delete_all_transactions


with open("secrets.json", 'r') as file:
    secrets = json.load(file)

YNAB_ACCESS_TOKEN = secrets["ynab_access_token"]


# CLI loop

while True:

    print("1. Print all category groups and categories")
    print("2. Print all transactions in a category")
    print("3. Delete all transactions in a category")
    print("4. Migrate all transactions from one category to another")
    print()
    choice = input("Enter your choice: ")

    if choice == "1":
        print()
        budget_id = input("Budget ID: ")
        print()
        print_categories(budget_id, YNAB_ACCESS_TOKEN)

    elif choice == "2":
        print()
        budget_id = input("Budget ID: ")
        category_id = input("Category ID: ")
        print_transactions(budget_id, category_id, YNAB_ACCESS_TOKEN)

    elif choice == "3":
        print()
        budget_id = input("Budget ID: ")
        category_id = input("Category ID: ")
        delete_all_transactions(budget_id, category_id, YNAB_ACCESS_TOKEN)

    elif choice == "4":
        print()
        #TODO: Figure out a way to implement the account_map in the CLI
        print("Sorry, can't actually use this through the CLI right now.")
        # start_budget_id = input("Starting budget ID: ")
        # start_category_id = input("Starting category ID: ")
        # end_budget_id = input("Ending budget ID: ")
        # end_category_id = input("Ending category ID: ")

    print("--------------------------------------------")
