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

def save_ynab_access_token(token, filepath):
    if os.path.exists(filepath):
        with open(filepath, "w+") as file:
            file_dict = json.load(file)
            file_dict['ynab_access_token'] = token
            json.dump(file_dict, file)
    else:
        with open(filepath, "w") as file:
            json.dump({"ynab_access_token": token}, file)

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

def category_groups_to_categories(category_groups:dict):
    categories = {}

    for group in category_groups.values():
        for category in group["categories"].items():
            categories[category[1]] = category[0]

    return categories

# r = get_categories("4Lg1oavXLOGMeMh5vMjpWbwyYORJJ_QYo3BocCIIz7Y", "13dc7d71-a3d0-4818-a53f-7707d14a293b")

# r = category_groups_to_categories(r)

# # print(json.dumps(r, indent=2))
# print(r)
