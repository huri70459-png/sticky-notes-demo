"""Run the sticky-notes app. Stores notes under %LOCALAPPDATA%\StickyNotes\notes.json"""
import os
import sys
from pathlib import Path

# Allow `python run.py` from the project root without installing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sticky_notes.app import NotesApp
from sticky_notes.store import NoteStore


def default_store_path() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    folder = Path(base) / "StickyNotes"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "notes.json"


if __name__ == "__main__":
    NotesApp(store=NoteStore(default_store_path())).mainloop()
