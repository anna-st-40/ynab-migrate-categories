import json
import requests
from cli_interface import validate_budget_choice
from funcs import print_categories

# Get authentication
with open("secrets.json", 'r') as file:
    secrets = json.load(file)

YNAB_ACCESS_TOKEN = secrets["ynab_access_token"]
headers = {"Authorization": f"Bearer {YNAB_ACCESS_TOKEN}"}


print("Welcome to YNAB Category Migration.\n")

# Get budgets
budget_response = requests.get(f"https://api.ynab.com/v1/budgets/", headers=headers).json()
budgets = {n["id"]:n["name"] for n in budget_response["data"]["budgets"]}

# Choose starting budget
print("Please select a budget to migrate FROM:")
for i, n in enumerate(budgets.values()):
    print(str(i+1)+". ", n)

start_budget_id = validate_budget_choice(budgets)

# Choose ending budget
print("Please select a budget to migrate TO:")
for i, n in enumerate(budgets.values()):
    print(str(i+1)+". ", n)

end_budget_id = validate_budget_choice(budgets)

print(f"Migrating from {budgets[start_budget_id]} to {budgets[end_budget_id]}.")

# # Display categories
# print_categories(start_budget_id, YNAB_ACCESS_TOKEN)