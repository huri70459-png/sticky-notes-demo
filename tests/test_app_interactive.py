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


def test_notes_have_delete_buttons(tmp_path: Path):
    """Each note should render with a Delete button."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="n1", text="test", color="yellow")
    app._refresh()
    buttons = [w for w in app.list_frame.winfo_children()
               if isinstance(w, tk.Frame)
               and any(isinstance(c, tk.Button) for c in w.winfo_children())]
    assert len(buttons) >= 1


def test_delete_note_removes_from_store(tmp_path: Path):
    """Calling delete_note should remove the note from the store."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="n1", text="test", color="yellow")
    store.add(id="n2", text="second", color="pink")
    app.delete_note("n1")
    assert app.note_count() == 1
    remaining = app.store.all()
    assert len(remaining) == 1
    assert remaining[0].id == "n2"


def test_edit_note_updates_text(tmp_path: Path):
    """Calling edit_note should update the note's text in the store."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="n1", text="old text", color="yellow")
    app._refresh()
    app.edit_note("n1", "new text")
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].text == "new text"
