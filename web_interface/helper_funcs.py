import os
import json
import requests

def verify_ynab_access_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.ynab.com/v1/user", headers=headers).json()

    if "error" in response:
        return False
    else:
        return True

def get_budgets(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.ynab.com/v1/budgets/", headers=headers).json()
    return {n["id"]:n["name"] for n in response["data"]["budgets"]}


def get_categories(token, budget_id):

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.ynab.com/v1/budgets/{budget_id}/categories", headers=headers).json()

    if "error" in response:
        print(response)

    else:
        d = {}
        for group in response["data"]["category_groups"]:
            d[group["id"]] = {"name":group["name"], "categories":{}}
            for category in group["categories"]:
                d[group["id"]]["categories"][category["id"]] = category["name"]
    
        return d
    
def get_accounts(token, budget_id):

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.ynab.com/v1/budgets/{budget_id}/accounts", headers=headers).json()

    if "error" in response:
        print(response)

    else:
        return {account['id']: account['name'] for account in response['data']['accounts']}