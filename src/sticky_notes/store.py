import json
import re
import uuid
from pathlib import Path
from .note import Note

# Pattern to match [[id]] wiki-style links
_LINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
# Pattern to match #tag hashtags
_TAG_RE = re.compile(r'#(\w+)')


class NoteStore:
    def __init__(self, path: Path):
        self.path = path

    def all(self) -> list[Note]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        notes = [Note(**n) for n in data]
        # Pinned notes always come first
        return sorted(notes, key=lambda n: (not n.pinned, n.id))

    def all_for_id(self, note_id: str) -> Note | None:
        """Return a single note by ID, or None if not found."""
        for n in self.all():
            if n.id == note_id:
                return n
        return None

    def search(self, query: str) -> list[Note]:
        """Return notes whose text contains the query (case-insensitive)."""
        if not query:
            return self.all()
        q = query.lower()
        return [n for n in self.all() if q in n.text.lower()]

    def add(self, *, id: str | None = None, text: str, color: str = "yellow",
            pinned: bool = False, width: int = 200, height: int = 100,
            content: str = "", always_on_top: bool = False,
            links: list | None = None, tags: list | None = None) -> Note:
        notes = self.all()
        new_note = Note(
            id=id or str(uuid.uuid4()),
            text=text,
            color=color,
            pinned=pinned,
            width=width,
            height=height,
            content=content,
            always_on_top=always_on_top,
        )
        # Auto-parse [[id]] links from text
        if links is not None:
            new_note.links = list(links)
        else:
            new_note.links = self._extract_links(text)
        # Auto-parse #tags from text
        if tags is not None:
            new_note.tags = list(tags)
        else:
            new_note.tags = self._extract_tags(text)
        notes.append(new_note)
        self._write(notes)
        return new_note

    def _extract_links(self, text: str) -> list[str]:
        """Extract [[id]] wiki-links from text."""
        matches = _LINK_RE.findall(text)
        seen: set[str] = set()
        result: list[str] = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                result.append(m)
        return result

    def _extract_tags(self, text: str) -> list[str]:
        """Extract #tag hashtags from text."""
        matches = _TAG_RE.findall(text)
        seen: set[str] = set()
        result: list[str] = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                result.append(m)
        return result

    def _write(self, notes: list[Note]) -> None:
        data = [{"id": n.id, "text": n.text, "color": n.color, "pinned": n.pinned,
                 "width": n.width, "height": n.height, "content": n.content,
                 "always_on_top": n.always_on_top, "links": n.links, "tags": n.tags}
                for n in notes]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update(self, note_id: str, *, text: str | None = None,
               color: str | None = None, pinned: bool | None = None,
               width: int | None = None, height: int | None = None,
               content: str | None = None,
               always_on_top: bool | None = None,
               links: list | None = None,
               tags: list | None = None) -> None:
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
                if content is not None:
                    n.content = content
                if always_on_top is not None:
                    n.always_on_top = always_on_top
                if links is not None:
                    n.links = list(links)
                if tags is not None:
                    n.tags = list(tags)
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

    def toggle_always_on_top(self, note_id: str) -> None:
        """Flip the always_on_top flag for a note."""
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                n.always_on_top = not n.always_on_top
                break
        self._write(notes)

    def backlinks(self, note_id: str) -> list[Note]:
        """Return notes that link to the given note_id (backlinks)."""
        return [n for n in self.all() if note_id in n.links]

    def add_link(self, from_id: str, to_id: str) -> None:
        """Add a link from one note to another."""
        notes = self.all()  # fresh read from disk
        for n in notes:
            if n.id == from_id:
                if to_id not in n.links:
                    n.links.append(to_id)
                break
        self._write(notes)

    def filter_by_tag(self, tag: str) -> list[Note]:
        """Return notes that have the given tag."""
        return [n for n in self.all() if tag in n.tags]

    def all_tags(self) -> set[str]:
        """Return all unique tag names across all notes."""
        tags: set[str] = set()
        for n in self.all():
            tags.update(n.tags)
        return tags

    def add_tag(self, note_id: str, tag: str) -> None:
        """Add a tag to a note if it doesn't already have it."""
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                if tag not in n.tags:
                    n.tags.append(tag)
                break
        self._write(notes)

    def remove_tag(self, note_id: str, tag: str) -> None:
        """Remove a tag from a note."""
        notes = self.all()
        for n in notes:
            if n.id == note_id:
                if tag in n.tags:
                    n.tags.remove(tag)
                break
        self._write(notes)

    def export_markdown(self) -> str:
        """Export all notes as a markdown string."""
        lines: list[str] = ["# Sticky Notes Export", ""]
        for note in self.all():
            color_label = {"yellow": "⚠️", "pink": "❤️", "cyan": "💧"}.get(note.color, "")
            lines.append(f"## {note.text} {color_label}")
            if note.tags:
                lines.append(f"**Tags:** {' '.join(f'#{t}' for t in note.tags)}")
            if note.links:
                lines.append(f"**Links:** {' '.join(f'[[{l}]]' for l in note.links)}")
            if note.pinned:
                lines.append("**📌 Pinned**")
            if note.always_on_top:
                lines.append("**📌 Always-on-top**")
            lines.append("")
        return "\n".join(lines)

    def export_to_markdown_file(self, path: Path) -> None:
        """Write notes to a markdown file."""
        path.write_text(self.export_markdown(), encoding="utf-8")
