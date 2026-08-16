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

def test_store_updates_note_text(tmp_path: Path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    store.add(id="1", text="old", color="yellow")
    store.update("1", text="new")
    assert NoteStore(path).all()[0].text == "new"

def test_store_updates_note_color(tmp_path: Path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    store.add(id="1", text="x", color="yellow")
    store.update("1", color="blue")
    assert NoteStore(path).all()[0].color == "blue"

def test_store_deletes_note(tmp_path: Path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    store.add(id="1", text="x", color="yellow")
    store.add(id="2", text="y", color="pink")
    store.delete("1")
    remaining = NoteStore(path).all()
    assert len(remaining) == 1
    assert remaining[0].id == "2"
