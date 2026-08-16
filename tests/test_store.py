from pathlib import Path
from sticky_notes.store import NoteStore

def test_store_starts_empty_when_file_missing(tmp_path: Path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.all() == []

def test_store_saves_and_loads_note(tmp_path: Path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    store.add(id="1", text="buy milk", color="yellow")
    reloaded = NoteStore(path)
    notes = reloaded.all()
    assert len(notes) == 1
    assert notes[0].text == "buy milk"
