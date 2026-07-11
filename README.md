# SecureBank — Banking Workshop Application

A lightweight, browser-based banking application built with **Python · Flask · SQLite · Bootstrap 5**.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8 or higher |
| pip | ships with Python 3 |

---

## Quick Start

### 1. Clone / download the project

```bash
git clone https://github.com/flytanisha/bob-banking-app.git
cd bob-banking-app
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv BACKEND/venv
source BACKEND/venv/bin/activate

# Windows (Command Prompt)
python -m venv BACKEND\venv
BACKEND\venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv BACKEND\venv
BACKEND\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r BACKEND/requirements.txt
```

### 4. Start the application

```bash
python BACKEND/app.py
```

Open **http://127.0.0.1:5000** in your browser.

> The SQLite database (`BACKEND/bank.db`) is created and seeded automatically on first run — no manual setup needed.

---

## Test Credentials

| Username | Password | Starting Balance |
|---|---|---|
| `alice` | `password123` | $1,000.00 |
| `bob` | `password456` | $500.00 |

---

## Project Structure

```
bob-banking-app/
├── FRONTEND/
│   ├── templates/
│   │   ├── base.html        # Shared layout (navbar, flash messages)
│   │   ├── login.html       # Login form
│   │   ├── dashboard.html   # Balance display + deposit/withdraw forms
│   │   └── error.html       # 404 / 500 error page
│   └── static/
│       └── style.css        # Custom brand styles
│
├── BACKEND/
│   ├── app.py               # Flask entry point; all routes
│   ├── models.py            # Database layer (all SQL lives here)
│   ├── auth.py              # login_required decorator
│   ├── config.py            # Secret key, DB path, debug flag
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       ├── test_models.py   # Unit tests for the data-access layer
│       └── test_routes.py   # Integration tests for all routes
│
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## Running the Tests

```bash
# From the project root, with the virtual environment active:
python -m pytest BACKEND/tests/ -v
```

All tests use an in-memory SQLite database — `bank.db` is never modified by the test suite.

---

## Sharing on a Local Network (Workshop Demo)

The dev server binds to `0.0.0.0` by default, so other devices on the same Wi-Fi network can reach it via the host machine's local IP address on port 5000.  
**This is for workshop demonstrations only — not for internet exposure.**

---

## Production Notes

The Flask development server is not suitable for production use. Before deploying:

- Replace the `SECRET_KEY` with a long random string read from an environment variable.
- Set `DEBUG = False` in `config.py` (or via environment variable).
- Serve with **Gunicorn** (Linux/macOS) or **Waitress** (Windows) behind Nginx.
- Enable HTTPS and set `SESSION_COOKIE_SECURE = True`.
