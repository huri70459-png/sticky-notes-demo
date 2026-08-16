"""Shared pytest fixtures for sticky-notes tests.

Tkinter can only create ONE root Tk instance per process. Both test_app.py
and test_app_interactive.py need one, so we create it here once and reuse it.
"""
import pytest
import tkinter as tk
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def tk_root():
    """A single Tk root shared across all tests in the session."""
    root = tk.Tk()
    root.withdraw()
    yield root


@pytest.fixture
def mock_requests():
    """A mock HTTP requests module for testing sync backends.

    Returns a MagicMock so tests can inspect call_args, call_count, etc.
    """
    import sticky_notes.sync as sync_mod
    mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    mock.post.return_value = mock_resp
    mock.get.return_value = mock_resp
    sync_mod._requests = mock
    yield mock
    sync_mod._requests = None