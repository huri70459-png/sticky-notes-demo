"""Authentication backends for Sticky Notes.

Provides pluggable authentication: MicrosoftAuth, GitHubAuth, GoogleAuth.
Each provider implements OAuth2 device flow for desktop apps.
"""
import abc
import json
import pathlib
from typing import Any


class AuthBackend(abc.ABC):
    """Abstract base class for authentication backends."""

    @abc.abstractmethod
    def get_device_code(self) -> dict[str, Any]:
        """Request a device code for user authorization."""

    @abc.abstractmethod
    def get_token(self, device_code: str, user_code: str) -> dict[str, Any]:
        """Poll for token using device code."""

    @abc.abstractmethod
    def login(self) -> str | None:
        """Start OAuth flow and return access token."""

    @abc.abstractmethod
    def logout(self) -> None:
        """Clear stored token."""

    @abc.abstractmethod
    def get_token_cached(self) -> str | None:
        """Return cached token if exists."""

    @abc.abstractmethod
    def is_authenticated(self) -> bool:
        """Check if authenticated."""


class OAuthProvider(abc.ABC):
    """Base class for OAuth2 device flow providers."""

    device_code_url: str = ""
    scope: str = ""
    client_id: str = ""

    def __init__(self, client_id: str = "sticky-notes"):
        self.client_id = client_id

    @abc.abstractmethod
    def _get_device_code_params(self) -> dict[str, str]:
        """Return query params for device code request."""

    @abc.abstractmethod
    def _poll_token_url(self) -> str:
        """Return URL to poll for token."""

    def get_device_code(self) -> dict[str, Any]:
        """Request device code from provider."""
        params = self._get_device_code_params()
        # In real implementation: HTTP POST to device_code_url
        return {"device_code": "mock", "user_code": "MockCode", "verification_uri": "https://example.com"}

    def get_token(self, device_code: str) -> dict[str, Any]:
        """Poll for token."""
        return {"access_token": "mock_token", "expires_in": 3600}


class MicrosoftAuth(OAuthProvider):
    """Microsoft OAuth2 device flow."""

    device_code_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    scope = "Notes.ReadWrite"

    def _get_device_code_params(self) -> dict[str, str]:
        return {"client_id": self.client_id, "scope": self.scope}

    def _poll_token_url(self) -> str:
        return "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

    def login(self) -> str | None:
        """Start Microsoft device flow — user must visit URL and enter code."""
        code_info = self.get_device_code()
        print(f"Visit: {code_info.get('verification_uri')}")
        print(f"Enter code: {code_info.get('user_code')}")
        # Poll for token
        token = self.get_token(code_info.get("device_code"))
        return token.get("access_token")

    def logout(self) -> None:
        """Clear Microsoft token."""
        pass

    def get_token_cached(self) -> str | None:
        """Check for cached Microsoft token."""
        return None

    def is_authenticated(self) -> bool:
        """Check if Microsoft-authenticated."""
        return self.get_token_cached() is not None


class GitHubAuth(OAuthProvider):
    """GitHub OAuth2 device flow."""

    device_code_url = "https://github.com/login/device"
    scope = "user"

    def _get_device_code_params(self) -> dict[str, str]:
        return {"client_id": self.client_id, "scope": self.scope}

    def _poll_token_url(self) -> str:
        return "https://github.com/login/oauth/access_token"

    def login(self) -> str | None:
        """Start GitHub device flow."""
        code_info = self.get_device_code()
        print(f"Visit: {code_info.get('verification_uri')}")
        print(f"Enter code: {code_info.get('user_code')}")
        token = self.get_token(code_info.get("device_code"))
        return token.get("access_token")

    def logout(self) -> None:
        pass

    def get_token_cached(self) -> str | None:
        return None

    def is_authenticated(self) -> bool:
        return self.get_token_cached() is not None


class GoogleAuth(OAuthProvider):
    """Google OAuth2 device flow."""

    device_code_url = "https://oauth2.googleapis.com/device"
    scopes = ["openid", "https://www.googleapis.com/auth/notes"]

    def _get_device_code_params(self) -> dict[str, str]:
        return {"client_id": self.client_id, "scope": " ".join(self.scopes)}

    def _poll_token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    def login(self) -> str | None:
        """Start Google device flow."""
        code_info = self.get_device_code()
        print(f"Visit: {code_info.get('verification_uri')}")
        print(f"Enter code: {code_info.get('user_code')}")
        token = self.get_token(code_info.get("device_code"))
        return token.get("access_token")

    def logout(self) -> None:
        pass

    def get_token_cached(self) -> str | None:
        return None

    def is_authenticated(self) -> bool:
        return self.get_token_cached() is not None