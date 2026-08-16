import tkinter as tk
from pathlib import Path
from sticky_notes.app import NotesApp
from sticky_notes.store import NoteStore

# Single root reused across tests — Tk() can only be instantiated once
_ROOT = tk.Tk()
_ROOT.withdraw()  # hide the window during tests


def test_add_note_button_appears(tmp_path: Path):
    """An Entry and a Button for adding notes must exist."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    assert app.add_entry is not None
    assert app.add_button is not None


def test_add_note_creates_note_and_refreshes(tmp_path: Path):
    """Typing text and calling add_note should create a persisted note."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    app.add_entry.delete(0, tk.END)
    app.add_entry.insert(0, "New sticky note")
    app.add_note()
    assert app.note_count() == 1
    assert app.store.all()[0].text == "New sticky note"


def test_add_note_empty_text_does_nothing(tmp_path: Path):
    """Empty or whitespace-only input should not create a note."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    app.add_entry.delete(0, tk.END)
    app.add_note()  # nothing typed
    assert app.note_count() == 0
