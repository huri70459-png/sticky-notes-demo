import tkinter as tk
from .store import NoteStore

class NotesApp:
    def __init__(self, *, store: NoteStore):
        self.store = store
        self.root = tk.Tk()
        self.root.title("Sticky Notes")
        self._build_ui()

    def _build_ui(self) -> None:
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh()

    def _refresh(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for note in self.store.all():
            label = tk.Label(self.list_frame, text=note.text, bg=note.color, width=20, height=5)
            label.pack(pady=4)

    def note_count(self) -> int:
        return len(self.store.all())

    def mainloop(self) -> None:
        self.root.mainloop()
