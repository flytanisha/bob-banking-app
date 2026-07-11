"""
auth.py — authentication helpers.

Provides the `login_required` decorator, which redirects unauthenticated
users to /login. Apply it to every protected route.
"""
import functools
from flask import session, redirect, url_for


def login_required(f):
    """Route decorator that enforces an active session."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper
