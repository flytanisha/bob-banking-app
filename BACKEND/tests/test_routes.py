"""
test_routes.py — integration tests for all Flask routes.

Each test uses Flask's built-in test client. The model helpers are
monkey-patched to use an isolated in-memory SQLite connection so the
real bank.db is never touched.
"""
import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
import app as app_module


@pytest.fixture()
def client():
    _conn = sqlite3.connect(":memory:")
    _conn.row_factory = sqlite3.Row
    models.init_db(conn=_conn)
    models.seed_db(conn=_conn)

    _originals = {
        "get_customer_by_username":   models.get_customer_by_username,
        "get_account_by_customer_id": models.get_account_by_customer_id,
        "update_balance":             models.update_balance,
    }

    models.get_customer_by_username   = lambda u, conn=None:        _originals["get_customer_by_username"](u, conn=_conn)
    models.get_account_by_customer_id = lambda cid, conn=None:      _originals["get_account_by_customer_id"](cid, conn=_conn)
    models.update_balance             = lambda aid, bal, conn=None: _originals["update_balance"](aid, bal, conn=_conn)

    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret-key"

    with app_module.app.test_client() as test_client:
        yield test_client

    for name, fn in _originals.items():
        setattr(models, name, fn)
    _conn.close()


def _login(client, username="alice", password="password123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


class TestRoot:
    def test_root_redirects_to_login(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


class TestLogin:
    def test_get_login_renders_form(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Log In" in resp.data

    def test_valid_credentials_redirect_to_dashboard(self, client):
        resp = client.post(
            "/login",
            data={"username": "alice", "password": "password123"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]

    def test_wrong_password_shows_error(self, client):
        resp = _login(client, password="wrongpassword")
        assert b"Invalid username or password" in resp.data

    def test_unknown_username_shows_generic_error(self, client):
        resp = _login(client, username="nobody", password="irrelevant")
        assert b"Invalid username or password" in resp.data

    def test_empty_username_shows_error(self, client):
        resp = client.post(
            "/login",
            data={"username": "", "password": "password123"},
            follow_redirects=True,
        )
        assert b"Username is required" in resp.data

    def test_empty_password_shows_error(self, client):
        resp = client.post(
            "/login",
            data={"username": "alice", "password": ""},
            follow_redirects=True,
        )
        assert b"Password is required" in resp.data

    def test_already_logged_in_redirects_to_dashboard(self, client):
        _login(client)
        resp = client.get("/login", follow_redirects=False)
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]


class TestSessionGuard:
    def test_dashboard_without_session_redirects_to_login(self, client):
        resp = client.get("/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_deposit_without_session_redirects_to_login(self, client):
        resp = client.post("/deposit", data={"amount": "50"}, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_withdraw_without_session_redirects_to_login(self, client):
        resp = client.post("/withdraw", data={"amount": "50"}, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_dashboard_after_login_returns_200(self, client):
        _login(client)
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        assert b"Alice" in resp.data


class TestDashboard:
    def test_shows_balance(self, client):
        _login(client)
        resp = client.get("/dashboard")
        assert b"1000.00" in resp.data

    def test_shows_customer_name(self, client):
        _login(client)
        resp = client.get("/dashboard")
        assert b"Alice" in resp.data


class TestDeposit:
    def test_valid_deposit_increases_balance(self, client):
        _login(client)
        client.post("/deposit", data={"amount": "200"}, follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"1200.00" in resp.data

    def test_decimal_deposit(self, client):
        _login(client)
        client.post("/deposit", data={"amount": "50.75"}, follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"1050.75" in resp.data

    def test_zero_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/deposit", data={"amount": "0"}, follow_redirects=True)
        assert b"greater than zero" in resp.data

    def test_negative_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/deposit", data={"amount": "-10"}, follow_redirects=True)
        assert b"greater than zero" in resp.data

    def test_non_numeric_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/deposit", data={"amount": "abc"}, follow_redirects=True)
        assert b"must be a number" in resp.data

    def test_empty_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/deposit", data={"amount": ""}, follow_redirects=True)
        assert b"required" in resp.data


class TestWithdraw:
    def test_valid_withdrawal_decreases_balance(self, client):
        _login(client)
        client.post("/withdraw", data={"amount": "300"}, follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"700.00" in resp.data

    def test_withdraw_entire_balance_reaches_zero(self, client):
        _login(client)
        client.post("/withdraw", data={"amount": "1000"}, follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"0.00" in resp.data

    def test_overdraft_shows_error(self, client):
        _login(client)
        resp = client.post("/withdraw", data={"amount": "5000"}, follow_redirects=True)
        assert b"Insufficient funds" in resp.data

    def test_overdraft_does_not_change_balance(self, client):
        _login(client)
        client.post("/withdraw", data={"amount": "5000"}, follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"1000.00" in resp.data

    def test_zero_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/withdraw", data={"amount": "0"}, follow_redirects=True)
        assert b"greater than zero" in resp.data

    def test_non_numeric_amount_shows_error(self, client):
        _login(client)
        resp = client.post("/withdraw", data={"amount": "xyz"}, follow_redirects=True)
        assert b"must be a number" in resp.data


class TestLogout:
    def test_logout_redirects_to_login(self, client):
        _login(client)
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_logout_clears_session(self, client):
        _login(client)
        client.get("/logout")
        resp = client.get("/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_logout_without_session_redirects_to_login(self, client):
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


class TestErrorHandlers:
    def test_404_returns_error_page(self, client):
        resp = client.get("/nonexistent-path")
        assert resp.status_code == 404
        assert b"404" in resp.data
