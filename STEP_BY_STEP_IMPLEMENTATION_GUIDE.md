# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** This guide follows the phased roadmap defined in `IMPLEMENTATION_PLAN.md`.  
> All instructions are written in plain English describing *what to do and why* — not verbatim code.

---

## Step 1 — Environment Setup

### 1.1 Verify Python is Installed
Confirm that Python 3.8 or higher is available. Check `pip` is also available.

### 1.2 Create a Virtual Environment
Navigate into `BACKEND/` and create a virtual environment with `python -m venv venv`. Activate it.

### 1.3 Create the Requirements File
Create `BACKEND/requirements.txt` listing `flask==3.0.3`, `werkzeug==3.0.3`, `pytest==8.2.2`.

### 1.4 Install Dependencies
Run `pip install -r BACKEND/requirements.txt`.

### 1.5 Confirm Flask is Working
Run `python BACKEND/app.py` and open http://127.0.0.1:5000.

---

## Step 2 — Backend Implementation

### 2.1 Configure the Application (`config.py`)
Define `SECRET_KEY`, `DATABASE` path, and `DEBUG = True`.

### 2.2 Initialise the Database (`models.py`)
- `get_db_connection()` — returns open `sqlite3.Connection` with `row_factory = sqlite3.Row`.
- `init_db()` — creates `customers` and `accounts` tables with `CREATE TABLE IF NOT EXISTS`.
- `seed_db()` — inserts two test customers if the table is empty.
- `get_customer_by_username(username)`, `get_account_by_customer_id(customer_id)`, `update_balance(account_id, new_balance)`.

### 2.3 Build the Authentication Helpers (`auth.py`)
`login_required` decorator — checks `session['user_id']`; redirects to `/login` if absent.

### 2.4 Create the Flask Application and Routes (`app.py`)
Routes: `GET /`, `GET+POST /login`, `GET /dashboard`, `POST /deposit`, `POST /withdraw`, `GET /logout`. Error handlers for 404 and 500.

---

## Step 3 — Frontend Implementation

### 3.1 Base Layout (`base.html`)
Bootstrap 5 CDN, navbar with conditional Logout link, flash message loop, `{% block content %}`.

### 3.2 Login Page (`login.html`)
Centred Bootstrap card with username/password form posting to `/login`.

### 3.3 Dashboard Page (`dashboard.html`)
Greeting, balance card, two-column deposit/withdraw forms.

### 3.4–3.5 Deposit / Withdraw Forms
`POST /deposit` and `POST /withdraw`, `amount` input with `min="0.01"` and `step="0.01"`.

---

## Step 4 — Integration

- Flask `template_folder` → `FRONTEND/templates/`, `static_folder` → `FRONTEND/static/`.
- Form `action` and input `name` attributes match route definitions exactly.
- Routes call `models.py` helpers — no raw SQL in route handlers.

---

## Step 5 — Validation Rules

| Check | Route | Error message |
|---|---|---|
| Username not empty | POST /login | "Username is required." |
| Password not empty | POST /login | "Password is required." |
| Credentials match | POST /login | "Invalid username or password." |
| Amount not empty | POST /deposit, /withdraw | "Amount is required." |
| Amount is numeric | POST /deposit, /withdraw | "Amount must be a number." |
| Amount > 0 | POST /deposit, /withdraw | "Amount must be greater than zero." |
| Amount ≤ balance | POST /withdraw | "Insufficient funds." |

---

## Step 6 — Testing

```bash
python -m pytest BACKEND/tests/ -v
```

- `test_models.py` — unit tests for all `models.py` helpers using in-memory SQLite.
- `test_routes.py` — integration tests for all routes using Flask test client.

---

## Step 7 — Deployment

```bash
python BACKEND/app.py
```

For production: Gunicorn + Nginx, `DEBUG=False`, `SECRET_KEY` from env var, HTTPS.
