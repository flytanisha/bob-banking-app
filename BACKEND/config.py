"""
config.py — centralised application configuration.

All environment-specific settings live here.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "f3a9b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
)

DATABASE = os.path.join(BASE_DIR, "bank.db")

DEBUG = True
