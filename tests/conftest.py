"""Shared pytest fixtures for sticky-notes tests.

Tkinter can only create ONE root Tk instance per process. Both test_app.py
and test_app_interactive.py need one, so we create it here once and reuse it.
"""
import pytest
import tkinter as tk

@pytest.fixture(scope="session")
def tk_root():
    """A single Tk root shared across all tests in the session."""
    root = tk.Tk()
    root.withdraw()  # hide window during tests
    yield root
    # Don't destroy — let the process exit clean it up
