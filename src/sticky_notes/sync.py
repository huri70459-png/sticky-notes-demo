"""Sync backends for Sticky Notes.

Provides a pluggable sync layer: GitSync (git repo) and SimpleAPISync (REST API).
Each backend implements push() and pull() to synchronize the local JSON store
with a remote source.
"""
import abc
import json
import subprocess
from pathlib import Path
from .note import Note
from .store import NoteStore


class SyncBackend(abc.ABC):
    """Abstract base class for sync backends."""

    @abc.abstractmethod
    def push(self, notes: list[Note]) -> None:
        """Push local notes to the remote source."""

    @abc.abstractmethod
    def pull(self) -> list[Note]:
        """Pull notes from the remote source and return them."""


class GitSync(SyncBackend):
    """Sync via a local or remote git repository."""

    def __init__(self, repo_path: Path, store: NoteStore):
        self.repo_path = repo_path
        self.store = store
        self.notes_file = "notes.json"

    def _run_git(self, args: list[str]) -> str:
        """Run a git command in the repo directory."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {args}: {result.stderr}")
        return result.stdout.strip()

    def _init_repo(self) -> None:
        """Initialize the git repo if it doesn't exist."""
        if not (self.repo_path / ".git").exists():
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self._run_git(["init"])
            self._run_git(["config", "user.name", "StickyNotes"])
            self._run_git(["config", "user.email", "notes@sticky.app"])

    def push(self, notes: list[Note] | None = None) -> None:
        """Push local notes to the git repo."""
        self._init_repo()
        if notes is None:
            notes = self.store.all()

        # Write notes as JSON
        data = [{"id": n.id, "text": n.text, "color": n.color, "pinned": n.pinned,
                 "width": n.width, "height": n.height, "content": n.content,
                 "always_on_top": n.always_on_top, "links": n.links, "tags": n.tags,
                 "order": n.order}
                for n in notes]
        notes_path = self.repo_path / self.notes_file
        notes_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        self._run_git(["add", self.notes_file])
        self._run_git(["commit", "-m", "Sync notes"])

    def pull(self) -> list[Note]:
        """Pull notes from the git repo into the local store."""
        if not (self.repo_path / ".git").exists():
            return self.store.all()

        try:
            self._run_git(["pull"])
        except RuntimeError:
            pass  # No remote configured — local-only repo

        notes_path = self.repo_path / self.notes_file
        if not notes_path.exists():
            return []

        data = json.loads(notes_path.read_text(encoding="utf-8"))
        notes = [Note(**n) for n in data]
        # Overwrite local store with remote state
        self.store._write(notes)
        return notes

    def is_dirty(self) -> bool:
        """Check if the local store has changes not yet pushed."""
        result = self._run_git(["status", "--porcelain"])
        return bool(result)


class SimpleAPISync(SyncBackend):
    """Sync via a REST API endpoint (Tier D)."""

    def __init__(self, store: NoteStore, endpoint: str, api_key: str | None = None):
        self.store = store
        self.endpoint = endpoint
        self.api_key = api_key
        self._timeout = 30

    @property
    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _serialize(self, notes: list[Note]) -> list[dict]:
        return [{"id": n.id, "text": n.text, "color": n.color, "pinned": n.pinned,
                 "width": n.width, "height": n.height, "content": n.content,
                 "always_on_top": n.always_on_top, "links": n.links,
                 "tags": n.tags, "order": n.order}
                for n in notes]

    def push(self, notes: list[Note] | None = None) -> None:
        """Push local notes to the REST API."""
        import requests as _base_requests
        # Allow test mock injection via module-level _requests
        import sticky_notes.sync as _self
        req = getattr(_self, "_requests", _base_requests)
        if notes is None:
            notes = self.store.all()
        data = self._serialize(notes)
        req.post(self.endpoint, json=data, headers=self._headers,
                 timeout=self._timeout)

    def pull(self) -> list[Note]:
        """Pull notes from the REST API and update local store."""
        import requests as _base_requests
        import sticky_notes.sync as _self
        req = getattr(_self, "_requests", _base_requests)
        resp = req.get(self.endpoint, headers=self._headers,
                       timeout=self._timeout)
        data = resp.json()
        if not isinstance(data, list):
            data = []
        notes = [Note(**n) for n in data]
        self.store._write(notes)
        return notes
