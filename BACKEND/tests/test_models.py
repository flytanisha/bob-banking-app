"""
test_models.py — unit tests for the data-access layer.

All tests use an in-memory SQLite database; bank.db is never touched.
"""
import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
from werkzeug.security import check_password_hash


@pytest.fixture()
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    models.init_db(conn=conn)
    models.seed_db(conn=conn)
    yield conn
    conn.close()


class TestSeeding:
    def test_seed_creates_two_customers(self, db):
        count = db.execute("SELECT COUNT(*) AS cnt FROM customers").fetchone()["cnt"]
        assert count == 2

    def test_seed_creates_two_accounts(self, db):
        count = db.execute("SELECT COUNT(*) AS cnt FROM accounts").fetchone()["cnt"]
        assert count == 2

    def test_seed_is_idempotent(self, db):
        models.seed_db(conn=db)
        count = db.execute("SELECT COUNT(*) AS cnt FROM customers").fetchone()["cnt"]
        assert count == 2

    def test_passwords_are_hashed(self, db):
        customer = models.get_customer_by_username("alice", conn=db)
        assert customer["password_hash"] != "password123"
        assert check_password_hash(customer["password_hash"], "password123")


class TestGetCustomerByUsername:
    def test_returns_row_for_existing_user(self, db):
        customer = models.get_customer_by_username("alice", conn=db)
        assert customer is not None
        assert customer["username"] == "alice"

    def test_returns_none_for_unknown_user(self, db):
        result = models.get_customer_by_username("nobody", conn=db)
        assert result is None

    def test_lookup_is_case_sensitive(self, db):
        result = models.get_customer_by_username("Alice", conn=db)
        assert result is None


class TestGetAccountByCustomerId:
    def test_returns_account_for_known_customer(self, db):
        customer = models.get_customer_by_username("alice", conn=db)
        account = models.get_account_by_customer_id(customer["id"], conn=db)
        assert account is not None
        assert account["customer_id"] == customer["id"]

    def test_alice_starting_balance(self, db):
        customer = models.get_customer_by_username("alice", conn=db)
        account = models.get_account_by_customer_id(customer["id"], conn=db)
        assert account["balance"] == 1000.00

    def test_bob_starting_balance(self, db):
        customer = models.get_customer_by_username("bob", conn=db)
        account = models.get_account_by_customer_id(customer["id"], conn=db)
        assert account["balance"] == 500.00

    def test_returns_none_for_unknown_customer_id(self, db):
        result = models.get_account_by_customer_id(9999, conn=db)
        assert result is None


class TestUpdateBalance:
    def test_balance_is_written_correctly(self, db):
        customer = models.get_customer_by_username("alice", conn=db)
        account = models.get_account_by_customer_id(customer["id"], conn=db)
        models.update_balance(account["id"], 1250.50, conn=db)
        updated = models.get_account_by_customer_id(customer["id"], conn=db)
        assert updated["balance"] == 1250.50

    def test_balance_can_be_set_to_zero(self, db):
        customer = models.get_customer_by_username("bob", conn=db)
        account = models.get_account_by_customer_id(customer["id"], conn=db)
        models.update_balance(account["id"], 0.0, conn=db)
        updated = models.get_account_by_customer_id(customer["id"], conn=db)
        assert updated["balance"] == 0.0

    def test_update_does_not_affect_other_accounts(self, db):
        alice = models.get_customer_by_username("alice", conn=db)
        alice_acct = models.get_account_by_customer_id(alice["id"], conn=db)
        models.update_balance(alice_acct["id"], 9999.99, conn=db)
        bob = models.get_customer_by_username("bob", conn=db)
        bob_acct = models.get_account_by_customer_id(bob["id"], conn=db)
        assert bob_acct["balance"] == 500.00
