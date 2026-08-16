"""Authentication module for Sticky Notes.

OAuth2 device flow providers (Microsoft/GitHub/Google) + AuthBackend ABC.
"""
import abc


class AuthBackend(abc.ABC):
    """Abstract base class for authentication backends."""
    @abc.abstractmethod
    def get_device_code(self) -> dict:
        """Request a device code for user authorization."""
    @abc.abstractmethod
    def get_token(self, device_code: str) -> dict:
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
    scopes: list[str] = []
    client_id: str = ""

    def __init__(self, client_id: str = "sticky-notes"):
        self.client_id = client_id
        self._cached_token: str | None = None

    @abc.abstractmethod
    def _get_device_code_params(self) -> dict:
        """Return query params for device code request."""
    @abc.abstractmethod
    def _poll_token_url(self) -> str:
        """Return URL to poll for token."""

    def get_device_code(self) -> dict:
        params = self._get_device_code_params()
        return {"device_code": "mock", "user_code": "MockCode",
                "verification_uri": "https://example.com"}

    def get_token(self, device_code: str) -> dict:
        return {"access_token": "mock_token", "expires_in": 3600}

    def login(self) -> str | None:
        code_info = self.get_device_code()
        print(f"Visit: {code_info['verification_uri']}")
        print(f"Enter code: {code_info['user_code']}")
        token = self.get_token(code_info.get("device_code"))
        self._cached_token = token.get("access_token")
        return token.get("access_token")

    def logout(self) -> None:
        self._cached_token = None

    def get_token_cached(self) -> str | None:
        return self._cached_token

    def is_authenticated(self) -> bool:
        return self._cached_token is not None


class MicrosoftAuth(OAuthProvider):
    device_code_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    scope = "Notes.ReadWrite"
    def _get_device_code_params(self):
        return {"client_id": self.client_id, "scope": self.scope}
    def _poll_token_url(self):
        return "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"


class GitHubAuth(OAuthProvider):
    device_code_url = "https://github.com/login/device"
    scope = "user"
    def _get_device_code_params(self):
        return {"client_id": self.client_id, "scope": self.scope}
    def _poll_token_url(self):
        return "https://github.com/login/oauth/access_token"


class GoogleAuth(OAuthProvider):
    device_code_url = "https://oauth2.googleapis.com/device"
    scopes = ["openid", "https://www.googleapis.com/auth/notes"]
    def _get_device_code_params(self):
        return {"client_id": self.client_id, "scope": " ".join(self.scopes)}
    def _poll_token_url(self):
        return "https://oauth2.googleapis.com/token"