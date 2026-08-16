"""Authentication tests for Sticky Notes.

Tests for AuthBackend, OAuth providers, and CloudSync with auth.
"""
from pathlib import Path

import pytest
from unittest.mock import MagicMock


def test_auth_backend_is_abstract():
    """AuthBackend should be an abstract base class — cannot instantiate."""
    from sticky_notes.auth import AuthBackend
    with pytest.raises(TypeError):
        AuthBackend()


def test_auth_backend_has_required_methods():
    """AuthBackend ABC should declare login, logout, get_token_cached, is_authenticated."""
    from sticky_notes.auth import AuthBackend
    assert hasattr(AuthBackend, "login")
    assert hasattr(AuthBackend, "logout")
    assert hasattr(AuthBackend, "get_token_cached")
    assert hasattr(AuthBackend, "is_authenticated")


def test_microsoft_auth_provider():
    """MicrosoftAuth should expose device flow URL and scope."""
    from sticky_notes.auth import MicrosoftAuth
    assert MicrosoftAuth.device_code_url == "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    assert MicrosoftAuth.scope == "Notes.ReadWrite"


def test_github_auth_provider():
    """GitHubAuth should expose device flow URL and scope."""
    from sticky_notes.auth import GitHubAuth
    assert GitHubAuth.device_code_url == "https://github.com/login/device"
    assert GitHubAuth.scope == "user"


def test_google_auth_provider():
    """GoogleAuth should expose device flow URL with openid scope."""
    from sticky_notes.auth import GoogleAuth
    assert GoogleAuth.device_code_url == "https://oauth2.googleapis.com/device"
    assert "openid" in GoogleAuth.scopes


def test_microsoft_auth_login():
    """MicrosoftAuth.login() should return a token string."""
    from sticky_notes.auth import MicrosoftAuth
    mock_req = MagicMock()
    mock_req.post.return_value = MagicMock(status_code=200,
        json=lambda: {"access_token": "ms-token-123", "expires_in": 3600})
    import sticky_notes.auth as auth_mod
    auth_mod._requests = mock_req
    try:
        provider = MicrosoftAuth(client_id="test")
        token = provider.login()
        assert isinstance(token, str)
        assert len(token) > 0
    finally:
        auth_mod._requests = None


def test_microsoft_auth_logout_clears_token():
    """MicrosoftAuth.logout() should clear cached token."""
    from sticky_notes.auth import MicrosoftAuth
    provider = MicrosoftAuth(client_id="test")
    provider._cached_token = "ms-token"
    assert provider.get_token_cached() == "ms-token"
    provider.logout()
    assert provider.get_token_cached() is None


def test_github_auth_login():
    """GitHubAuth.login() should return a token string."""
    from sticky_notes.auth import GitHubAuth
    mock_req = MagicMock()
    mock_req.post.return_value = MagicMock(status_code=200,
        json=lambda: {"access_token": "gh-token-456", "expires_in": 3600})
    import sticky_notes.auth as auth_mod
    auth_mod._requests = mock_req
    try:
        provider = GitHubAuth(client_id="test")
        token = provider.login()
        assert isinstance(token, str)
        assert len(token) > 0
    finally:
        auth_mod._requests = None


def test_github_auth_logout_clears_token():
    """GitHubAuth.logout() should clear cached token."""
    from sticky_notes.auth import GitHubAuth
    provider = GitHubAuth(client_id="test")
    provider._cached_token = "gh-token"
    assert provider.get_token_cached() == "gh-token"
    provider.logout()
    assert provider.get_token_cached() is None


def test_google_auth_login():
    """GoogleAuth.login() should return a token string."""
    from sticky_notes.auth import GoogleAuth
    mock_req = MagicMock()
    mock_req.post.return_value = MagicMock(status_code=200,
        json=lambda: {"access_token": "google-token-789", "expires_in": 3600})
    import sticky_notes.auth as auth_mod
    auth_mod._requests = mock_req
    try:
        provider = GoogleAuth(client_id="test")
        token = provider.login()
        assert isinstance(token, str)
        assert len(token) > 0
    finally:
        auth_mod._requests = None


def test_google_auth_logout_clears_token():
    """GoogleAuth.logout() should clear cached token."""
    from sticky_notes.auth import GoogleAuth
    provider = GoogleAuth(client_id="test")
    provider._cached_token = "google-token"
    assert provider.get_token_cached() == "google-token"
    provider.logout()
    assert provider.get_token_cached() is None


def test_is_authenticated_reflects_token_state():
    """is_authenticated should return True when token cached."""
    from sticky_notes.auth import GoogleAuth
    provider = GoogleAuth(client_id="test")
    assert provider.is_authenticated() is False
    provider._cached_token = "tok"
    assert provider.is_authenticated() is True


def test_cloud_sync_is_sync_backend():
    """CloudSync should be a SyncBackend."""
    from sticky_notes.sync import CloudSync, SyncBackend
    assert issubclass(CloudSync, SyncBackend)


def test_cloud_sync_init():
    """CloudSync should accept store, endpoint, and auth provider."""
    from sticky_notes.sync import CloudSync
    from sticky_notes.auth import GoogleAuth
    store = None
    provider = GoogleAuth(client_id="test")
    sync = CloudSync(store, "https://api.example.com/notes", provider)
    assert sync.endpoint == "https://api.example.com/notes"
    assert isinstance(sync.auth_provider, GoogleAuth)
    assert sync._headers()["Content-Type"] == "application/json"


def test_cloud_sync_push_includes_auth_token():
    """CloudSync push should POST with OAuth Bearer token in Authorization header."""
    from sticky_notes.sync import CloudSync
    from sticky_notes.auth import GoogleAuth
    import unittest.mock as mock

    provider = GoogleAuth(client_id="test")
    provider._cached_token = "google-abc-123"
    store = None

    mock_req = mock.MagicMock()
    mock_resp = mock.MagicMock(status_code=200)
    mock_req.post.return_value = mock_resp
    import sticky_notes.sync as sync_mod
    sync_mod._requests = mock_req
    try:
        notes = [{"id": "1", "text": "test", "color": "yellow",
                  "pinned": False, "width": 200, "height": 100,
                  "content": "", "always_on_top": False,
                  "links": [], "tags": [], "order": 0}]
        sync = CloudSync(store, "https://api.example.com/notes", provider)
        sync.push(notes)

        assert mock_req.post.call_args[0][0] == "https://api.example.com/notes"
        assert mock_req.post.call_args[1]["headers"]["Authorization"] == "Bearer google-abc-123"
    finally:
        sync_mod._requests = None


def test_cloud_sync_pull_includes_auth_token():
    """CloudSync pull should GET with OAuth Bearer token."""
    from sticky_notes.sync import CloudSync
    from sticky_notes.auth import MicrosoftAuth
    import unittest.mock as mock

    provider = MicrosoftAuth(client_id="test")
    provider._cached_token = "ms-xdf-456"
    store = None

    captured = {}
    mock_resp = mock.MagicMock(status_code=200)
    mock_resp.json.return_value = [{"id": "1", "text": "remote note", "color": "yellow",
                     "pinned": False, "width": 200, "height": 100,
                     "content": "", "always_on_top": False,
                     "links": [], "tags": [], "order": 0}]

    mock_req = mock.MagicMock()
    mock_req.get.return_value = mock_resp
    import sticky_notes.sync as sync_mod
    sync_mod._requests = mock_req
    try:
        sync = CloudSync(store, "https://api.example.com/notes", provider)
        notes = sync.pull()
        assert len(notes) == 1
        assert notes[0].text == "remote note"
        assert mock_req.get.call_args[0][0] == "https://api.example.com/notes"
        assert mock_req.get.call_args[1]["headers"]["Authorization"] == "Bearer ms-xdf-456"
    finally:
        sync_mod._requests = None


def test_cloud_sync_falls_back_to_api_key():
    """CloudSync should use api_key if no auth token cached."""
    from sticky_notes.sync import CloudSync
    from sticky_notes.auth import GoogleAuth
    import unittest.mock as mock

    provider = GoogleAuth(client_id="test")
    provider._cached_token = None
    store = None

    captured = {}
    mock_req = mock.MagicMock()
    mock_resp = mock.MagicMock(status_code=200)
    mock_req.post.return_value = mock_resp
    import sticky_notes.sync as sync_mod
    sync_mod._requests = mock_req
    try:
        notes = [{"id": "1", "text": "test", "color": "yellow",
                  "pinned": False, "width": 200, "height": 100,
                  "content": "", "always_on_top": False,
                  "links": [], "tags": [], "order": 0}]
        sync = CloudSync(store, "https://api.example.com/notes", provider,
                         api_key="api-key-789")
        sync.push(notes)

        assert mock_req.post.call_args[1]["headers"]["Authorization"] == "Bearer api-key-789"
        assert mock_req.post.call_args[1]["headers"]["Content-Type"] == "application/json"
    finally:
        sync_mod._requests = None