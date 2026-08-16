import tkinter as tk
from sticky_notes.app import NotesApp
from sticky_notes.store import NoteStore
from pathlib import Path

# Single root reused across tests — Tk() can only be instantiated once
_ROOT = tk.Tk()
_ROOT.withdraw()


def test_app_starts_with_no_notes(tmp_path: Path):
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    assert app.note_count() == 0
