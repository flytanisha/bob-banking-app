"""
app.py — Flask application entry point.

Defines all URL routes, wires together config / models / auth, and
points Flask at the FRONTEND templates and static folders.

Usage (development):
    python BACKEND/app.py
"""
import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
)
from werkzeug.security import check_password_hash

import config
import models
from auth import login_required

_backend_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_backend_dir)

app = Flask(
    __name__,
    template_folder=os.path.join(_project_root, "FRONTEND", "templates"),
    static_folder=os.path.join(_project_root, "FRONTEND", "static"),
)
app.secret_key = config.SECRET_KEY
app.debug = config.DEBUG

models.init_db()
models.seed_db()


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username:
        flash("Username is required.", "danger")
        return render_template("login.html")
    if not password:
        flash("Password is required.", "danger")
        return render_template("login.html")

    customer = models.get_customer_by_username(username)
    if customer is None or not check_password_hash(customer["password_hash"], password):
        flash("Invalid username or password.", "danger")
        return render_template("login.html")

    session["user_id"] = customer["id"]
    session["username"] = customer["username"]
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    customer_id = session["user_id"]
    customer = models.get_customer_by_username(session["username"])
    account = models.get_account_by_customer_id(customer_id)
    return render_template(
        "dashboard.html",
        customer_name=customer["username"].capitalize(),
        balance=account["balance"],
    )


@app.route("/deposit", methods=["POST"])
@login_required
def deposit():
    amount_raw = request.form.get("amount", "").strip()
    if not amount_raw:
        flash("Amount is required.", "danger")
        return redirect(url_for("dashboard"))
    try:
        amount = float(amount_raw)
    except ValueError:
        flash("Amount must be a number.", "danger")
        return redirect(url_for("dashboard"))
    if amount <= 0:
        flash("Amount must be greater than zero.", "danger")
        return redirect(url_for("dashboard"))
    account = models.get_account_by_customer_id(session["user_id"])
    new_balance = round(account["balance"] + amount, 2)
    models.update_balance(account["id"], new_balance)
    flash(f"Deposit of ${amount:,.2f} successful. New balance: ${new_balance:,.2f}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/withdraw", methods=["POST"])
@login_required
def withdraw():
    amount_raw = request.form.get("amount", "").strip()
    if not amount_raw:
        flash("Amount is required.", "danger")
        return redirect(url_for("dashboard"))
    try:
        amount = float(amount_raw)
    except ValueError:
        flash("Amount must be a number.", "danger")
        return redirect(url_for("dashboard"))
    if amount <= 0:
        flash("Amount must be greater than zero.", "danger")
        return redirect(url_for("dashboard"))
    account = models.get_account_by_customer_id(session["user_id"])
    if amount > account["balance"]:
        flash("Insufficient funds.", "danger")
        return redirect(url_for("dashboard"))
    new_balance = round(account["balance"] - amount, 2)
    models.update_balance(account["id"], new_balance)
    flash(f"Withdrawal of ${amount:,.2f} successful. New balance: ${new_balance:,.2f}.", "success")
    return redirect(url_for("dashboard"))


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", code=500, message="An unexpected error occurred."), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
