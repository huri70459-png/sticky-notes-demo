import json
import uuid
from pathlib import Path
from .note import Note

class NoteStore:
    def __init__(self, path: Path):
        self.path = path

    def all(self) -> list[Note]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        notes = [Note(**n) for n in data]
        # Pinned notes always come first
        return sorted(notes, key=lambda n: not n.pinned)

    def search(self, query: str) -> list[Note]:
        """Return notes whose text contains the query (case-insensitive)."""
        if not query:
            return self.all()
        q = query.lower()
        return [n for n in self.all() if q in n.text.lower()]

    def add(self, *, id: str | None = None, text: str, color: str = "yellow",
            pinned: bool = False, width: int = 200, height: int = 100) -> Note:
        notes = self.all()
        new_note = Note(
            id=id or str(uuid.uuid4()),
            text=text,
            color=color,
            pinned=pinned,
            width=width,
            height=height,
        )
        notes.append(new_note)
        self._write(notes)
        return new_note

    def _write(self, notes: list[Note]) -> None:
        data = [{"id": n.id, "text": n.text, "color": n.color, "pinned": n.pinned,
                 "width": n.width, "height": n.height}
                for n in notes]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update(self, note_id: str, *, text: str | None = None,
               color: str | None = None, pinned: bool | None = None,
               width: int | None = None, height: int | None = None) -> None:
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                if text is not None:
                    n.text = text
                if color is not None:
                    n.color = color
                if pinned is not None:
                    n.pinned = pinned
                if width is not None:
                    n.width = width
                if height is not None:
                    n.height = height
                break
        self._write(notes)

    def delete(self, note_id: str) -> None:
        notes = [n for n in self.all() if n.id != note_id]
        self._write(notes)

    def toggle_pin(self, note_id: str) -> None:
        """Flip the pinned flag for a note."""
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                n.pinned = not n.pinned
                break
        self._write(notes)
