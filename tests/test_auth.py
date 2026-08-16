"""Authentication tests for Sticky Notes.

Tests for AuthBackend, OAuth providers, and auth UI.
"""
from pathlib import Path

import pytest
from sticky_notes.auth import AuthBackend


def test_auth_backend_is_abstract():
    """AuthBackend should be an abstract base class."""
    from sticky_notes.auth import AuthBackend
    with pytest.raises(TypeError):
        AuthBackend()


def test_auth_backend_has_required_methods():
    """AuthBackend ABC should define login, logout, token, is_authenticated."""
    from sticky_notes.auth import AuthBackend
    assert hasattr(AuthBackend, "login")
    assert hasattr(AuthBackend, "logout")
    assert hasattr(AuthBackend, "get_token")
    assert hasattr(AuthBackend, "is_authenticated")


def test_microsoft_auth_provider():
    """MicrosoftAuth should have device flow URL."""
    from sticky_notes.auth import MicrosoftAuth
    provider = MicrosoftAuth(client_id="test")
    assert MicrosoftAuth.device_code_url == "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    assert provider.scope == "Notes.ReadWrite"


def test_github_auth_provider():
    """GitHubAuth should have device flow URL."""
    from sticky_notes.auth import GitHubAuth
    provider = GitHubAuth(client_id="test")
    assert GitHubAuth.device_code_url == "https://github.com/login/device"
    assert provider.scope == "user"


def test_google_auth_provider():
    """GoogleAuth should have device flow URL."""
    from sticky_notes.auth import GoogleAuth
    provider = GoogleAuth(client_id="test")
    assert GoogleAuth.device_code_url == "https://oauth2.googleapis.com/device"
    assert "openid" in provider.scopes