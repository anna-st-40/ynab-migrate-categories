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
    if verify_ynab_access_token(YNAB_ACCESS_TOKEN):
        return redirect(url_for('budget_selection'))

@app.route("/budget-selection")
def budget_selection():
    if not YNAB_ACCESS_TOKEN:
        return redirect(url_for("authentication"))
    else:
        budgets = get_budgets(YNAB_ACCESS_TOKEN)
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
    global category_migrations
    category_migrations = request.form["category-migrations"]
    return redirect(url_for('account_selection'))

@app.route("/account-selection")
def account_selection():
    start_accounts = get_accounts(YNAB_ACCESS_TOKEN, start_budget)
    end_accounts = get_accounts(YNAB_ACCESS_TOKEN, end_budget)

    return render_template("account_selection_page.html", 
                           start_accounts=start_accounts, 
                           end_accounts=end_accounts)

@app.route("/submit-accounts", methods=["POST"])
def submit_accounts():
    global account_migrations
    account_migrations = request.form["account-migrations"]

    return account_migrations

#TODO: Next steps: choose flag color
#TODO: Use cookies instead of global variables