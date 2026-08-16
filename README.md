# Sticky Notes (Hermes demo)

Tiny Windows desktop sticky-notes app, built end-to-end through the Hermes flow:
**idea → spec → TDD → build → review → commit**.

## Run

```bash
.venv/Scripts/python run.py
```

Notes persist at `%LOCALAPPDATA%\StickyNotes\notes.json`.

## Test

```bash
.venv/Scripts/python -m pytest tests/ -v
```

## Stack

- Python 3.11 + Tkinter (stdlib)
- JSON file storage
- pytest
