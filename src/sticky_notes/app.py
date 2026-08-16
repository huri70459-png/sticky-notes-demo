import tkinter as tk
from .store import NoteStore

class NotesApp:
    def __init__(self, *, store: NoteStore, root: tk.Tk | None = None):
        self.store = store
        self.root = root if root is not None else tk.Tk()
        self.root.title("Sticky Notes")
        self._build_ui()

    def _build_ui(self) -> None:
        self.current_color = "yellow"
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=8)

        self.add_entry = tk.Entry(self.form_frame, width=30)
        self.add_entry.pack(side="left", padx=(0, 8))

        self.add_button = tk.Button(self.form_frame, text="Add", command=self.add_note)
        self.add_button.pack(side="left")

        self._refresh()

    def add_note(self) -> None:
        text = self.add_entry.get().strip()
        if text:
            self.store.add(text=text, color=self.current_color)
            self.add_entry.delete(0, tk.END)
            self._refresh()

    def _refresh(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for note in self.store.all():
            frame = tk.Frame(self.list_frame, relief="raised", bd=1)

            edit_entry = tk.Entry(frame, width=20, fg=note.color)
            edit_entry.insert(0, note.text)
            edit_entry.pack(side="left")

            save_btn = tk.Button(
                frame, text="Save", width=5,
                command=lambda nid=note.id, e=edit_entry: self.edit_note(nid, e.get()),
            )
            save_btn.pack(side="left", padx=(4, 0))

            del_btn = tk.Button(frame, text="×", width=3,
                                command=lambda nid=note.id: self.delete_note(nid))
            del_btn.pack(side="right")

            frame.pack(pady=4)

    def edit_note(self, note_id: str, new_text: str) -> None:
        self.store.update(note_id, text=new_text)
        self._refresh()

    def delete_note(self, note_id: str) -> None:
        self.store.delete(note_id)
        self._refresh()

    def note_count(self) -> int:
        return len(self.store.all())

    def mainloop(self) -> None:
        self.root.mainloop()
