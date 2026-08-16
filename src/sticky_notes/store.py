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
        return [Note(**n) for n in data]

    def add(self, *, id: str | None = None, text: str, color: str = "yellow") -> Note:
        notes = self.all()
        new_note = Note(
            id=id or str(uuid.uuid4()),
            text=text,
            color=color,
        )
        notes.append(new_note)
        self._write(notes)
        return new_note

    def _write(self, notes: list[Note]) -> None:
        data = [{"id": n.id, "text": n.text, "color": n.color} for n in notes]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update(self, note_id: str, *, text: str | None = None, color: str | None = None) -> None:
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                if text is not None:
                    n.text = text
                if color is not None:
                    n.color = color
                break
        self._write(notes)

    def delete(self, note_id: str) -> None:
        notes = [n for n in self.all() if n.id != note_id]
        self._write(notes)
