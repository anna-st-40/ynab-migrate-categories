from flask import Flask, request, session, redirect, render_template, url_for
import requests

from helper_funcs import *

app = Flask(__name__)

YNAB_ACCESS_TOKEN = None

@app.route("/")
def home():
    if not YNAB_ACCESS_TOKEN:
        return redirect(url_for("authentication"))
    else:
        return redirect(url_for('budget_selection'))

@app.route("/authentication")
def authentication():
    return render_template("authentication_page.html")

@app.route("/submit-token", methods=["POST"])
def submit_token():
    global YNAB_ACCESS_TOKEN
    YNAB_ACCESS_TOKEN = request.form["token"]
    # TODO: Verify token
    return redirect(url_for('budget_selection'))

@app.route("/budget-selection")
def budget_selection():
    if not YNAB_ACCESS_TOKEN:
        return redirect(url_for("authentication"))
    else:
        response = requests.get(f"https://api.ynab.com/v1/budgets/", headers={"Authorization": f"Bearer {YNAB_ACCESS_TOKEN}"}).json()
        budgets = {n["id"]:n["name"] for n in response["data"]["budgets"]}
        return render_template("budget_selection_page.html", budgets=budgets)

@app.route("/submit-budgets", methods=["POST"])
def submit_budgets():
    global start_budget
    start_budget = request.form["start_budget"]
    global end_budget
    end_budget = request.form["end_budget"]
    return redirect(url_for('category_selection'))

@app.route("/category-selection")
def category_selection():
    if not YNAB_ACCESS_TOKEN:
        return redirect(url_for("authentication"))
    else:
        start_categories = get_categories(YNAB_ACCESS_TOKEN, start_budget)
        end_categories = get_categories(YNAB_ACCESS_TOKEN, end_budget)
        
        return render_template("category_selection_page.html", 
                            start_categories=start_categories, 
                            end_categories=end_categories)

@app.route("/submit-categories", methods=["POST"])
def submit_categories():
    migrations = request.form["category-migrations"]
    return migrations

#TODO: Next steps: choose account counterparts & choose flag color
#TODO: Use cookies instead of global variables

@app.route("/account-selection")
def account_selection():
    pass

@app.route("/submit-accounts", methods=["POST"])
def submit_accounts():
    pass
