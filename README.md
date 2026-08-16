# Sticky Notes (Hermes demo)

A Microsoft Sticky Notes competitor built end-to-end through the **Hermes Agent flow**:
idea → spec → TDD → build → review → commit.

## Features

- **Add** notes with typeahead + Enter or button
- **Edit** note text inline via multi-line Text widget
- **Delete** notes with a × button
- **Color picker** — yellow, blue, green, pink, lavender, cyan
- **Per-note resizing** — notes auto-size to content
- **Rich text** — `**bold**` and `*italic*` markdown in notes
- **Search** — live filter as you type (Ctrl+F)
- **Pin** — pin important notes to the top (📌)
- **Always-on-top** — keep window on top (📌 Pin Window)
- **Transparency** — slider from 10% to 100% (💧)
- **Dark mode** — toggle with 🌙/☀️
- **Note linking** — `[[note-id]]` wiki-links with backlinks
- **Tags** — `#tag` parsing, filter by tag
- **Keyboard shortcuts** — Ctrl+N (new), Ctrl+S (save), Ctrl+D (delete), Ctrl+F (search)
- **Markdown export** — File → Export Markdown
- **Optional sync** — GitSync backend (push/pull to git repo)
- **MS Sticky Notes aesthetic** — Segoe UI font, colored note cards, toolbar design

## Run

```bash
cd ~/sticky-notes-demo
.venv/Scripts/python run.py
```

Notes persist at `%LOCALAPPDATA%\StickyNotes\notes.json`.

## Test

```bash
.venv/Scripts/python -m pytest tests/ -v
# 58 passed
```

## Stack

- Python 3.11 + Tkinter (stdlib — no install)
- JSON file storage
- pytest (58 tests across 4 modules)
- Optional: git for sync

## Architecture

- `src/sticky_notes/note.py` — `Note` dataclass (14 fields: id, text, color, pinned, width, height, content, always_on_top, links, tags)
- `src/sticky_notes/store.py` — `NoteStore` (CRUD + search + pin + tags + links + markdown export)
- `src/sticky_notes/app.py` — `NotesApp` (Tkinter UI, keyboard shortcuts, dark mode, transparency)
- `src/sticky_notes/sync.py` — `SyncBackend` ABC + `GitSync` implementation
- `tests/` — 58 tests across 4 modules
- `redesign/sticky-notes-redesign.html` — HTML prototype of the UI
