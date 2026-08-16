import tkinter as tk
from pathlib import Path
from sticky_notes.app import NotesApp
from sticky_notes.store import NoteStore


def test_add_note_button_appears(tmp_path: Path, tk_root):
    """An Entry and a Button for adding notes must exist."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    assert app.add_entry is not None
    assert app.add_button is not None


def test_add_note_creates_note_and_refreshes(tmp_path: Path, tk_root):
    """Typing text and calling add_note should create a persisted note."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.add_entry.delete(0, tk.END)
    app.add_entry.insert(0, "New sticky note")
    app.add_note()
    assert app.note_count() == 1
    assert app.store.all()[0].text == "New sticky note"


def test_add_note_empty_text_does_nothing(tmp_path: Path, tk_root):
    """Empty or whitespace-only input should not create a note."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.add_entry.delete(0, tk.END)
    app.add_note()
    assert app.note_count() == 0


def test_notes_have_delete_buttons(tmp_path: Path, tk_root):
    """Each note should render with a Delete button."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="test", color="yellow")
    app._refresh()
    buttons = [w for w in app.list_frame.winfo_children()
               if isinstance(w, tk.Frame)
               and any(isinstance(c, tk.Button) for c in w.winfo_children())]
    assert len(buttons) >= 1


def test_delete_note_removes_from_store(tmp_path: Path, tk_root):
    """Calling delete_note should remove the note from the store."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="test", color="yellow")
    store.add(id="n2", text="second", color="pink")
    app.delete_note("n1")
    assert app.note_count() == 1
    remaining = app.store.all()
    assert len(remaining) == 1
    assert remaining[0].id == "n2"


def test_edit_note_updates_text(tmp_path: Path, tk_root):
    """Calling edit_note should update the note's text in the store."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="old text", color="yellow")
    app._refresh()
    app.edit_note("n1", "new text")
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].text == "new text"


# ---- Color picker tests ----

PRESET_COLORS = ["yellow", "pink", "cyan"]


def test_color_picker_buttons_exist(tmp_path: Path, tk_root):
    """At least the preset color buttons must be rendered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    color_btns = [w for w in app.form_frame.winfo_children()
                  if getattr(w, "_color", False)]
    assert len(color_btns) >= 3


def test_set_color_changes_current_color(tmp_path: Path, tk_root):
    """Selecting a color should update the current color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.set_color("pink")
    assert app.current_color == "pink"


def test_add_note_uses_selected_color(tmp_path: Path, tk_root):
    """A new note should be stored with the currently selected color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
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


def test_search_filter_updates_ui(tmp_path: Path, tk_root):
    """Setting search_var and calling apply_search should filter visible notes."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="1", text="buy milk", color="yellow")
    store.add(id="2", text="call mom", color="pink")
    app.search_var.set("milk")
    app.apply_search()
    assert app.filtered_count() == 1


def test_search_empty_shows_all(tmp_path: Path, tk_root):
    """Empty search query should show all notes."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
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


def test_pin_button_toggles_pin_state(tmp_path: Path, tk_root):
    """UI pin button should call store.toggle_pin."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="test", color="yellow")
    app._refresh()
    app.toggle_pin("n1")
    assert store.all()[0].pinned is True
    app.toggle_pin("n1")
    assert store.all()[0].pinned is False


# ---- Dark mode tests ----

def test_dark_mode_toggle_exists(tmp_path: Path, tk_root):
    """App should start in light mode with a toggle_dark_mode method."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    assert hasattr(app, "toggle_dark_mode")
    assert app.dark_mode is False


def test_toggle_dark_mode_flips_flag(tmp_path: Path, tk_root):
    """toggle_dark_mode should flip the dark_mode flag."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.toggle_dark_mode()
    assert app.dark_mode is True
    app.toggle_dark_mode()
    assert app.dark_mode is False


def test_toggle_dark_mode_changes_root_bg(tmp_path: Path, tk_root):
    """Dark mode should change the root window background color."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    light_bg = app.root.cget("bg")
    app.toggle_dark_mode()
    dark_bg = app.root.cget("bg")
    assert light_bg != dark_bg


# ---- Note sizing tests ----

def test_note_has_size_fields():
    """New Note should have width and height fields with defaults."""
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert hasattr(note, "width")
    assert hasattr(note, "height")
    assert hasattr(note, "always_on_top")


def test_note_default_size():
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert note.width > 0
    assert note.height > 0
    assert note.always_on_top is False


def test_store_saves_note_size(tmp_path: Path):
    """Note width/height should persist to JSON."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow", width=300, height=150)
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].width == 300
    assert reloaded.all()[0].height == 150


# ---- Always-on-top tests ----

def test_note_has_always_on_top(tmp_path: Path):
    """New notes should default to always_on_top=False."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    assert store.all()[0].always_on_top is False


def test_store_saves_always_on_top(tmp_path: Path):
    """always_on_top should persist to JSON."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow", always_on_top=True)
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].always_on_top is True


def test_toggle_always_on_top(tmp_path: Path):
    """toggle_always_on_top should flip the flag and persist."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    store.toggle_always_on_top("1")
    assert NoteStore(tmp_path / "notes.json").all()[0].always_on_top is True
    store.toggle_always_on_top("1")
    assert NoteStore(tmp_path / "notes.json").all()[0].always_on_top is False


# ---- Rich text tests ----

def test_note_has_content_field():
    """Note should have a content field for rich text (markdown)."""
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert hasattr(note, "content")
    assert note.content == ""


def test_store_saves_content(tmp_path: Path):
    """Content (markdown) should persist."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow", content="**bold** text")
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].content == "**bold** text"


def test_rich_text_applies_bold_tag(tmp_path: Path, tk_root):
    """Text containing **bold** should have 'bold' tag applied in the Text widget."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="test", color="yellow", content="**bold** text")
    app._refresh()
    # Get the text widget from the first note frame
    note_frame = app.list_frame.winfo_children()[0]
    text_widget = [w for w in note_frame.winfo_children() if isinstance(w, tk.Text)][0]
    # The bold tag should be applied to "bold"
    tags = text_widget.tag_names("1.0")
    assert "bold" in tags
