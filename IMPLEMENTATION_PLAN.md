# Banking Web Application — Implementation Plan

---

## 1. Solution Overview

### Objective
Build a lightweight, browser-based banking application that allows registered customers to securely log in, view their account balance, and perform basic fund transactions (deposit and withdrawal).

### Scope
| In Scope | Out of Scope |
|---|---|
| Customer login / logout | User self-registration |
| Balance inquiry | Multi-currency support |
| Deposit funds | Transfers between accounts |
| Withdraw funds | Admin / back-office portal |
| Session-based authentication | Two-factor authentication |
| Single-page dashboard | Transaction history / statements |

### Users
- **Customer** — a pre-created bank account holder who logs in, views their balance, and performs transactions.

### Functional Requirements
1. A customer must authenticate with a username and password before accessing any feature.
2. After login, the customer lands on a personalised dashboard showing their current balance.
3. The customer can deposit a positive amount; the balance updates immediately.
4. The customer can withdraw a positive amount up to the available balance; the balance updates immediately.
5. The customer can log out, which terminates the session.

### Non-Functional Requirements
| Attribute | Expectation |
|---|---|
| Security | Passwords stored as hashed values; session cookie used for auth state |
| Usability | Responsive layout that works on desktop and mobile (Bootstrap) |
| Simplicity | Minimal dependencies — no external services beyond SQLite |
| Portability | Runs locally with `python app.py`; no Docker or cloud infra required |

---

## 2. High-Level Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│            HTML + Bootstrap (FRONTEND/)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│               Python Flask (BACKEND/)                       │
│  /login  /logout  /dashboard  /deposit  /withdraw           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                              │
│                SQLite file (BACKEND/)                       │
│            bank.db  ── customers table                      │
│                      └─ accounts table                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Design

### Frontend Responsibilities
- Render all user-facing pages (login, dashboard, deposit/withdraw forms).
- Apply Bootstrap grid and component classes for a consistent, responsive layout.
- Display server-side flash messages (success / error feedback) returned by Flask.

### Backend Responsibilities
- Define URL routes and HTTP method handlers (GET / POST) for every feature.
- Enforce session-based authentication on every protected route.
- Validate all incoming data (field presence, numeric ranges) on the server side.
- Hash passwords at comparison time; never store or transmit plaintext passwords.

### Database Responsibilities
- Persist customer credentials (username + password hash).
- Persist account state (current balance, linked customer).
- The SQLite file lives inside the `BACKEND/` folder and is excluded from version control.

---

## 4. Folder Structure

```
bob-banking-app/
├── FRONTEND/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── error.html
│   └── static/
│       └── style.css
├── BACKEND/
│   ├── app.py
│   ├── models.py
│   ├── auth.py
│   ├── config.py
│   ├── requirements.txt
│   └── tests/
│       ├── test_models.py
│       └── test_routes.py
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## 5. Implementation Roadmap

### Phase 1 — Project Scaffold
### Phase 2 — Database Initialisation
### Phase 3 — Authentication (Login / Logout)
### Phase 4 — Dashboard & Balance View
### Phase 5 — Deposit & Withdraw
### Phase 6 — Styling & UX Polish
### Phase 7 — Validation & Testing
