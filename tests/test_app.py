from sticky_notes.app import NotesApp
from sticky_notes.store import NoteStore
from pathlib import Path

def test_app_starts_with_no_notes(tmp_path: Path):
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store)
    assert app.note_count() == 0
