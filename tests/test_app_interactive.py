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
               and any(isinstance(c, tk.Button)
                       for child in w.winfo_children()
                       for c in ([child] if isinstance(child, tk.Button)
                                 else (child.winfo_children() if isinstance(child, tk.Frame) else [])))]
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
                  for w2 in (w.winfo_children() if isinstance(w, tk.Frame) else [w])
                  if getattr(w2, "_color", False)]
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


# ---- Transparency tests ----

def test_app_has_transparency_slider(tmp_path: Path, tk_root):
    """App should have a transparency slider widget."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    assert hasattr(app, "alpha_var")
    sliders = [w for w in app.form_frame.winfo_children() if isinstance(w, tk.Scale)]
    assert len(sliders) >= 1


def test_set_transparency_changes_alpha(tmp_path: Path, tk_root):
    """Setting alpha should update the window's -alpha attribute."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.set_transparency(0.5)
    assert app.root.attributes("-alpha") == 0.5


def test_set_transparency_clamps_value(tmp_path: Path, tk_root):
    """Alpha values outside [0.1, 1.0] should be clamped."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.set_transparency(2.0)
    assert app.root.attributes("-alpha") == 1.0
    app.set_transparency(0.0)
    assert app.root.attributes("-alpha") == 0.1


# ---- Note linking tests ----

def test_note_has_links_field():
    """New Note should have an empty links list."""
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert hasattr(note, "links")
    assert note.links == []


def test_store_saves_links(tmp_path: Path):
    """Links should persist to JSON."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="A", text="note A", color="yellow", links=["B", "C"])
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].links == ["B", "C"]


def test_store_backlinks(tmp_path: Path):
    """backlinks should return notes that link to the given note."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="A", text="A", color="yellow", links=["B"])
    store.add(id="B", text="B", color="yellow", links=["C"])
    store.add(id="C", text="C", color="yellow")
    result = store.backlinks("B")
    assert len(result) == 1
    assert result[0].id == "A"


def test_store_add_link(tmp_path: Path):
    """Adding a link should persist."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="A", text="A", color="yellow")
    store.add(id="B", text="B", color="yellow")
    store.add_link("A", "B")
    assert "B" in store.all_for_id("A").links


def test_note_text_links_parsed(tmp_path: Path):
    """Notes with [[id]] syntax should auto-generate links on save."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="A", text="See [[B]] for details", color="yellow")
    note = store.all_for_id("A")
    assert "B" in note.links


# ---- Tag tests ----

def test_note_has_tags_field():
    """New Note should have an empty tags list."""
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert hasattr(note, "tags")
    assert note.tags == []


def test_store_saves_tags(tmp_path: Path):
    """Tags should persist to JSON."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="buy milk", color="yellow", tags=["groceries", "todo"])
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all()[0].tags == ["groceries", "todo"]


def test_filter_by_tag(tmp_path: Path):
    """filter_by_tag should return notes with that tag."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="buy milk", color="yellow", tags=["groceries"])
    store.add(id="2", text="feed cat", color="pink", tags=["personal"])
    store.add(id="3", text="buy bread", color="cyan", tags=["groceries"])
    result = store.filter_by_tag("groceries")
    assert len(result) == 2
    assert {n.id for n in result} == {"1", "3"}


def test_all_tags(tmp_path: Path):
    """all_tags should return unique tag names."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="a", color="yellow", tags=["todo", "work"])
    store.add(id="2", text="b", color="pink", tags=["work", "personal"])
    tags = store.all_tags()
    assert set(tags) == {"todo", "work", "personal"}


def test_add_tag(tmp_path: Path):
    """Adding a tag to a note should persist."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    store.add_tag("1", "urgent")
    assert "urgent" in store.all_for_id("1").tags


def test_tags_parsed_from_text(tmp_path: Path):
    """#tag in note text should auto-generate tags."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="buy milk #grocery #todo", color="yellow")
    note = store.all_for_id("1")
    assert "grocery" in note.tags
    assert "todo" in note.tags


# ---- Keyboard shortcut tests ----

def test_app_registers_ctrl_n(tmp_path: Path, tk_root):
    """Ctrl+N should be registered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    bindings = app.root.bind()
    assert "<Control-Key-n>" in bindings or "<Control-n>" in bindings

def test_app_registers_ctrl_s(tmp_path: Path, tk_root):
    """Ctrl+S should be registered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    bindings = app.root.bind()
    assert "<Control-Key-s>" in bindings or "<Control-s>" in bindings

def test_app_registers_ctrl_d(tmp_path: Path, tk_root):
    """Ctrl+D should be registered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    bindings = app.root.bind()
    assert "<Control-Key-d>" in bindings or "<Control-d>" in bindings

def test_app_registers_ctrl_f(tmp_path: Path, tk_root):
    """Ctrl+F should be registered."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    bindings = app.root.bind()
    assert "<Control-Key-f>" in bindings or "<Control-f>" in bindings


# ---- Markdown export tests ----

def test_export_to_markdown(tmp_path: Path):
    """NoteStore.export_markdown should produce valid markdown."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="buy milk #grocery", color="yellow", tags=["grocery"])
    store.add(id="A", text="See [[B]]", color="pink", links=["B"])
    md = store.export_markdown()
    assert "# buy milk" in md
    assert "Tags:" in md
    assert "# See [[B]]" in md


def test_export_to_markdown_file(tmp_path: Path):
    """export_to_markdown_file should write a .md file."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    out = tmp_path / "export.md"
    store.export_to_markdown_file(out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "# hello" in content


# ---- Sync tests ----

def test_git_sync_push_creates_repo(tmp_path: Path):
    """GitSync should initialize a git repo and push notes."""
    from sticky_notes.sync import GitSync
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="synced note", color="yellow")
    git_dir = tmp_path / "sync_repo"
    sync = GitSync(git_dir, store)
    sync.push()
    assert (git_dir / ".git").exists()
    files = list(git_dir.rglob("*.json"))
    assert len(files) >= 1


def test_git_sync_pull_returns_notes(tmp_path: Path):
    """GitSync.pull should retrieve notes from the repo."""
    from sticky_notes.sync import GitSync
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="hello", color="yellow")
    git_dir = tmp_path / "sync_repo"
    sync = GitSync(git_dir, store)
    sync.push()
    # Pull into a fresh store
    store2 = NoteStore(tmp_path / "notes2.json")
    sync2 = GitSync(git_dir, store2)
    notes = sync2.pull()
    assert len(notes) >= 1
    assert notes[0].text == "hello"


# ---- REST API sync tests ----

def test_api_sync_is_sync_backend(tmp_path: Path):
    """SimpleAPISync should be a SyncBackend."""
    from sticky_notes.sync import SimpleAPISync, SyncBackend
    assert issubclass(SimpleAPISync, SyncBackend)


def test_api_sync_push_to_endpoint(tmp_path: Path):
    """API sync should serialize notes and POST them."""
    from sticky_notes.sync import SimpleAPISync
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="api note", color="yellow")
    sync = SimpleAPISync(store, "https://api.example.com/notes")
    # Mock the HTTP call
    import sticky_notes.sync as sync_mod
    called = []
    original = sync_mod.requests if hasattr(sync_mod, "requests") else None

    class MockResponse:
        status_code = 200
        def json(self):
            return {"success": True}

    class MockRequests:
        @staticmethod
        def post(url, json=None, headers=None, timeout=None):
            called.append((url, json))
            return MockResponse()
        @staticmethod
        def get(url, headers=None, timeout=None):
            return MockResponse()

    sync_mod._requests = MockRequests()
    sync.push()
    assert len(called) >= 1
    assert called[0][0] == "https://api.example.com/notes"
    assert isinstance(called[0][1], list)


def test_api_sync_pull_returns_notes(tmp_path: Path):
    """API sync pull should GET and deserialize notes."""
    from sticky_notes.sync import SimpleAPISync
    store = NoteStore(tmp_path / "notes.json")
    sync = SimpleAPISync(store, "https://api.example.com/notes")
    import sticky_notes.sync as sync_mod

    class MockResponse:
        status_code = 200
        def json(self):
            return [{"id": "1", "text": "remote note", "color": "yellow",
                     "pinned": False, "width": 200, "height": 100,
                     "content": "", "always_on_top": False, "links": [],
                     "tags": [], "order": 0}]

    class MockRequests:
        @staticmethod
        def get(url, headers=None, timeout=None):
            return MockResponse()
        @staticmethod
        def post(url, json=None, headers=None, timeout=None):
            return MockResponse()

    sync_mod._requests = MockRequests()
    notes = sync.pull()
    assert len(notes) == 1
    assert notes[0].text == "remote note"


def test_git_sync_pull_gets_updates(tmp_path: Path):
    """GitSync should pull notes from the sync repo into the store."""
    from sticky_notes.sync import GitSync
    git_dir = tmp_path / "sync_repo"
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="local note", color="yellow")
    sync = GitSync(git_dir, store)
    sync.push()
    # Modify store locally, then pull to get remote state
    store.add(id="2", text="should be overwritten", color="pink")
    sync.pull()
    notes = store.all()
    ids = {n.id for n in notes}
    assert "1" in ids
    assert "2" not in ids  # local change overwritten by remote
    assert len(notes) == 1


def test_sync_backend_is_abstract():
    """SyncBackend should be an abstract base class."""
    from sticky_notes.sync import SyncBackend
    from pathlib import Path
    try:
        SyncBackend(Path("/tmp"))
        assert False, "Should not be able to instantiate abstract class"
    except TypeError:
        pass


# ---- Drag-to-reorder tests ----

def test_note_has_order_field():
    """Notes should have an order field for drag-to-reorder."""
    from sticky_notes.note import Note
    note = Note(id="1", text="hello", color="yellow")
    assert hasattr(note, "order")
    assert note.order == 0


def test_store_saves_order(tmp_path: Path):
    """Note order should persist to JSON."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="first", color="yellow", order=0)
    store.add(id="2", text="second", color="pink", order=1)
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all_for_id("1").order == 0
    assert reloaded.all_for_id("2").order == 1


def test_store_move_note_reorders(tmp_path: Path):
    """move_note should change a note's order and persist it."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="1", text="a", color="yellow", order=0)
    store.add(id="2", text="b", color="yellow", order=1)
    store.add(id="3", text="c", color="yellow", order=2)
    store.move_note("3", new_position=0)
    reloaded = NoteStore(tmp_path / "notes.json")
    assert reloaded.all_for_id("3").order == 0
    assert reloaded.all_for_id("1").order == 1
    assert reloaded.all_for_id("2").order == 2


def test_store_saves_reorder(tmp_path: Path):
    """move_note should persist reordered notes."""
    store = NoteStore(tmp_path / "notes.json")
    store.add(id="A", text="a", color="yellow")
    store.add(id="B", text="b", color="yellow")
    store.add(id="C", text="c", color="yellow")
    store.move_note("C", new_position=0)
    reloaded = NoteStore(tmp_path / "notes.json")
    orders = {n.id: n.order for n in reloaded.all()}
    assert orders["C"] == 0
    assert orders["A"] == 1
    assert orders["B"] == 2


# ---- Font size tests ----

def test_app_has_font_size_setting(tmp_path: Path, tk_root):
    """App should support font size selection."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    assert hasattr(app, "set_font_size")
    app.set_font_size("16px")
    assert app._font_size == "16px"


def test_app_has_move_note_method(tmp_path: Path, tk_root):
    """App should have move_note for drag-to-reorder."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="1", text="a", color="yellow")
    store.add(id="2", text="b", color="yellow")
    app.move_note("2", new_position=0)
    assert app.store.all()[0].id == "2"


# ---- Context menu tests ----

def test_app_has_context_menu(tmp_path: Path, tk_root):
    """App should have a context menu for right-click actions."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    assert hasattr(app, "show_context_menu")
    assert hasattr(app, "_context_menu")


# ---- Tag badge tests ----

def test_note_tags_rendered_as_badges(tmp_path: Path, tk_root):
    """Notes with tags should render tag badge labels."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="n1", text="test #work", color="yellow", tags=["work"])
    app._refresh()
    # Check for tag badge in the note frame (recursive search)
    note_frame = app.list_frame.winfo_children()[0]
    badges = []
    def find_labels(widget):
        for w in widget.winfo_children():
            if isinstance(w, tk.Label) and getattr(w, "_tag", ""):
                badges.append(w)
            if isinstance(w, tk.Frame):
                find_labels(w)
    find_labels(note_frame)
    assert len(badges) >= 1


# ---- Daily note tests ----

def test_store_can_create_daily_note(tmp_path: Path):
    """Store should support creating a daily note."""
    from datetime import date
    store = NoteStore(tmp_path / "notes.json")
    today = date.today().isoformat()
    store.add(id=f"daily-{today}", text=f"Daily Note: {today}",
              color="yellow", tags=["daily"], pinned=True)
    note = store.all_for_id(f"daily-{today}")
    assert note is not None
    assert "daily" in note.tags


def test_app_create_daily_note(tmp_path: Path, tk_root):
    """App should create a daily note for today."""
    from datetime import date
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    app.create_daily_note()
    today = date.today().isoformat()
    note = store.all_for_id(f"daily-{today}")
    assert note is not None
    assert "daily" in note.tags
    assert note.pinned is True


def test_backlinks_displayed_in_ui(tmp_path: Path, tk_root):
    """Notes with backlinks should display 'Linked from' label."""
    store = NoteStore(tmp_path / "notes.json")
    app = NotesApp(store=store, root=tk_root)
    store.add(id="A", text="links to B", color="yellow", content="See [[B]]", links=["B"])
    store.add(id="B", text="target note", color="yellow")
    app._refresh()
    # Note B should have a backlink label
    notes = app.store.all()
    b_frame = None
    for frame in app.list_frame.winfo_children():
        if frame._note_id == "B":
            b_frame = frame
            break
    # Find the backlink label
    labels = [w for w in b_frame.winfo_children() if isinstance(w, tk.Label)
              and "Linked from" in (w.cget("text") if hasattr(w, "cget") else "")]
    assert len(labels) >= 1
