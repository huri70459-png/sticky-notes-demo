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


# ---- Color picker tests ----

PRESET_COLORS = ["yellow", "pink", "cyan"]


def test_color_picker_buttons_exist(tmp_path: Path):
    """At least the preset color buttons must be rendered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    color_btns = [w for w in app.form_frame.winfo_children()
                  if getattr(w, "_color", False)]
    assert len(color_btns) >= 3


def test_set_color_changes_current_color(tmp_path: Path):
    """Selecting a color should update the current color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    app.set_color("pink")
    assert app.current_color == "pink"


def test_add_note_uses_selected_color(tmp_path: Path):
    """A new note should be stored with the currently selected color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    app.add_entry.delete(0, tk.END)
    app.add_entry.insert(0, "colored note")
    app.set_color("cyan")
    app.add_note()
    assert app.store.all()[0].color == "cyan"


# ---- Search tests ----

def test_store_search_filters_by_text(tmp_path: Path):
    """NoteStore.search should return notes whose text contains the query."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="buy milk", color="yellow")
    store.add(id="2", text="call mom", color="pink")
    store.add(id="3", text="milk powder", color="cyan")
    results = store.search("milk")
    assert len(results) == 2
    assert {n.id for n in results} == {"1", "3"}


def test_search_filter_updates_ui(tmp_path: Path):
    """Setting search_var and calling apply_search should filter visible notes."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="1", text="buy milk", color="yellow")
    store.add(id="2", text="call mom", color="pink")
    app.search_var.set("milk")
    app.apply_search()
    assert app.filtered_count() == 1


def test_search_empty_shows_all(tmp_path: Path):
    """Empty search query should show all notes."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="1", text="a", color="yellow")
    store.add(id="2", text="b", color="pink")
    app.search_var.set("")
    app.apply_search()
    assert app.filtered_count() == 2


# ---- Pin tests ----

def test_note_has_pinned_field(tmp_path: Path):
    """New notes should default to pinned=False."""
    store = NoteStore(tmp_path / "notes.json")
    note = store.add(id="1", text="hello", color="yellow")
    assert note.pinned is False


def test_toggle_pin_flips_state(tmp_path: Path):
    """toggle_pin should flip pinned state and persist it."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    store.toggle_pin("1")
    assert NoteStore(tmp_path / "notes.json").all()[0].pinned is True
    store.toggle_pin("1")
    assert NoteStore(tmp_path / "notes.json").all()[0].pinned is False


def test_store_all_sorted_pinned_first(tmp_path: Path):
    """Pinned notes should appear before unpinned ones."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="unpinned", color="yellow")
    store.add(id="2", text="pinned", color="pink")
    store.toggle_pin("2")
    notes = store.all()
    assert notes[0].id == "2"
    assert notes[1].id == "1"


def test_pin_button_toggles_pin_state(tmp_path: Path):
    """UI pin button should call store.toggle_pin."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    store.add(id="n1", text="test", color="yellow")
    app._refresh()
    app.toggle_pin("n1")
    assert store.all()[0].pinned is True
    app.toggle_pin("n1")
    assert store.all()[0].pinned is False


# ---- Dark mode tests ----

def test_dark_mode_toggle_exists(tmp_path: Path):
    """App should start in light mode with a toggle_dark_mode method."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    assert hasattr(app, "toggle_dark_mode")
    assert app.dark_mode is False


def test_toggle_dark_mode_flips_flag(tmp_path: Path):
    """toggle_dark_mode should flip the dark_mode flag."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    app.toggle_dark_mode()
    assert app.dark_mode is True
    app.toggle_dark_mode()
    assert app.dark_mode is False


def test_toggle_dark_mode_changes_root_bg(tmp_path: Path):
    """Dark mode should change the root window background color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=_ROOT)
    light_bg = app.root.cget("bg")
    app.toggle_dark_mode()
    dark_bg = app.root.cget("bg")
    assert light_bg != dark_bg
