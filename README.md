# Sticky Notes (Hermes demo)

A Windows desktop sticky-notes app built end-to-end through the **Hermes Agent flow**:
*idea → spec → TDD → build → review → commit*.

## Features

- **Add** notes with an Entry + Add button
- **Edit** note text inline via Entry + Save per note
- **Delete** notes with a × button
- **Color picker** — choose yellow, pink, or cyan for new notes
- **Search** — live filter as you type
- **Pin** — pin important notes to the top (📌)
- **Dark mode** — toggle with 🌙/☀️ button

## Run

```bash
cd ~/sticky-notes-demo
.venv/Scripts/python run.py
```

Notes persist at `%LOCALAPPDATA%\StickyNotes\notes.json`.

## Test

```bash
.venv/Scripts/python -m pytest tests/ -v
# 26 passed
```

## Stack

- Python 3.11 + Tkinter (stdlib — no install)
- JSON file storage
- pytest (26 tests)

## Architecture

- `src/sticky_notes/note.py` — `Note` dataclass (id, text, color, pinned)
- `src/sticky_notes/store.py` — `NoteStore` (CRUD + search + pin over JSON)
- `src/sticky_notes/app.py` — `NotesApp` (Tkinter UI, thin event handlers)
- `tests/` — 26 tests across 4 modules
