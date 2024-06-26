import requests
import json

def _format_transaction_row(account, date, payee, memo, amount):
    """
    Formats a transaction for printing as a row of a table.
    This works for the header as well.
    """

    # Define column widths
    col_widths = {
        "Account": 20,
        "Date": 12,
        "Payee": 20,
        "Memo": 60,
        "Amount": 10
    }

    # If amount is a number, format it properly
    try:
        int(amount)
        if amount >= 0:
            amount = f"${(amount/1000):,.2f}"
        else: 
            amount = f"-${(amount/-1000):,.2f}"
    except ValueError:
        pass

    # Convert NoneType into empty strings
    if not payee:
        payee = ""
    if not memo:
        memo = ""

    # Cut short memos that are too long
    if len(memo) > col_widths["Memo"] - 3:
        memo = memo[:col_widths["Memo"] - 3] + "..."

    # Cut short account names that are too long
    if len(account) > col_widths["Account"] - 3:
        account = account[:col_widths["Account"] - 3] + "..."

    # Cut short payees that are too long
    if len(payee) > col_widths["Payee"] - 3:
        payee = payee[:col_widths["Payee"] - 3] + "..."

    return f"{account:<{col_widths['Account']}} {date:<{col_widths['Date']}} {payee:<{col_widths['Payee']}} {memo:<{col_widths['Memo']}} {amount:>{col_widths['Amount']}}"


def print_transactions(budget_id: str, category_id: str, ynab_access_token: str):

    headers = {"Authorization": f"Bearer {ynab_access_token}"}
    response = requests.get(f"https://api.ynab.com/v1/budgets/{budget_id}/categories/{category_id}/transactions", headers=headers).json()

    print(_format_transaction_row("Account", "Date", "Payee", "Memo", "Amount"))
    for transaction in response["data"]["transactions"]:
        print(_format_transaction_row(transaction["account_name"], transaction["date"], transaction["payee_name"], transaction["memo"], transaction["amount"]))

def print_categories(budget_id: str, ynab_access_token: str):
    """
    Prints all category groups and their categories in a budget.
    """

    headers = {"Authorization": f"Bearer {ynab_access_token}"}
    response = requests.get(f"https://api.ynab.com/v1/budgets/{budget_id}/categories", headers=headers).json()

    if "error" in response:
        print(response)

    else:

        for group in response["data"]["category_groups"]:
            print(group["name"])
            for category in group["categories"]:
                print(" "*4+category["name"]+" ||| "+category["id"])


def delete_all_transactions(budget_id: str, category_id: str, ynab_access_token: str):
    """
    Deletes all transactions in the category.
    """

    headers = {"Authorization": f"Bearer {ynab_access_token}"}

    # Get the transaction id's
    response_getreq = requests.get(f"https://api.ynab.com/v1/budgets/{budget_id}/categories/{category_id}/transactions", headers=headers).json()
    transactions = [t["id"] for t in response_getreq["data"]["transactions"]]

    # Verify deletion
    input(f"Deleting {len(transactions)} transactions from category {category_id}. Press Enter to continue.")

    # Delete transactions
    for t in transactions:
        response_deletereq = requests.delete(f"https://api.ynab.com/v1/budgets/{budget_id}//transactions/{t}", headers=headers).json()
        if "error" in response_deletereq:
            print(response_deletereq)

    print(f"Deleted {len(transactions)} transactions from category {category_id}.")

def migrate_category(start_budget_id: str, start_category_id: str, end_budget_id: str, end_category_id: str, account_map: dict, moved_flag_color: str, ynab_access_token: str):
    """
    Copies all the transactions from one category in one budget to another category in another budget.

    start_budget_id: ID of budget to be copied from.
    start_category_id: ID of category to be copied from.
    end_budget_id: ID of budget to be copied to.
    end_category_id: ID of category to be copied to.
    account_map: A dictionary mapping account IDs in the start budget to account IDs in the end budget
    moved_flag_color: What color to flag the transactions that have been moved.
    ynab_access_token: Personal YNAB access token.
    """
    headers = {"Authorization": f"Bearer {ynab_access_token}"}

    # Get the transactions
    response_get = requests.get(f"https://api.ynab.com/v1/budgets/{start_budget_id}/categories/{start_category_id}/transactions", headers=headers).json()

    # Format the transactions into the proper JSON format
    post_request_json = {"transactions": []}

    for transaction in response_get["data"]["transactions"]:
        t_dict = {
            "account_id": account_map[transaction["account_id"]],
            "date": transaction["date"],
            "amount": transaction["amount"],
            "payee_id": transaction["payee_id"],
            "payee_name": transaction["payee_name"],
            "category_id": end_category_id,
            "memo": transaction["memo"],
            "cleared": transaction["cleared"],
            "approved": transaction["approved"],
            "flag_color": moved_flag_color

        }

        post_request_json["transactions"].append(t_dict)

    # Add the transactions
    response_post = requests.post(f"https://api.ynab.com/v1/budgets/{end_budget_id}/transactions", headers=headers, data=json.dumps(post_request_json)).json()

    # Inform user of result
    if "error" in response_post:
        print(response_post)
    else:
        print(f"Successfully copied {len(post_request_json['transactions'])} transactions. Transaction copies have been flagged {moved_flag_color}.")