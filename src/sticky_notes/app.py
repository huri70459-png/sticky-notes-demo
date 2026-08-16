import tkinter as tk
from .store import NoteStore

class NotesApp:
    def __init__(self, *, store: NoteStore, root: tk.Tk | None = None):
        self.store = store
        self.root = root if root is not None else tk.Tk()
        self.root.title("Sticky Notes")
        self.current_color = "yellow"
        self.search_var = tk.StringVar()
        self._search_results: list | None = None
        self.dark_mode = False
        self._build_ui()

    def _build_ui(self) -> None:
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=8)

        self.add_entry = tk.Entry(self.form_frame, width=30)
        self.add_entry.pack(side="left", padx=(0, 8))

        self.add_button = tk.Button(self.form_frame, text="Add", command=self.add_note)
        self.add_button.pack(side="left", padx=(0, 8))

        for color in ("yellow", "pink", "cyan"):
            b = tk.Button(self.form_frame, text="", width=3, bg=color,
                          command=lambda c=color: self.set_color(c))
            b._color = True  # marker for test discovery
            b.pack(side="left", padx=2)

        search_label = tk.Label(self.form_frame, text="Search:")
        search_label.pack(side="left", padx=(16, 4))
        search_entry = tk.Entry(self.form_frame, textvariable=self.search_var, width=15)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_search())

        self.dark_mode_btn = tk.Button(self.form_frame, text="🌙 Dark",
                                       command=self.toggle_dark_mode, width=8)
        self.dark_mode_btn.pack(side="right", padx=(8, 0))

        self._apply_theme()
        self._refresh()

    def _apply_theme(self) -> None:
        if self.dark_mode:
            self.root.configure(bg="#2b2b2b")
            self.dark_mode_btn.configure(text="☀️ Light")
        else:
            self.root.configure(bg="#f0f0f0")
            self.dark_mode_btn.configure(text="🌙 Dark")

    def toggle_dark_mode(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self._refresh()

    def set_color(self, color: str) -> None:
        self.current_color = color

    def apply_search(self) -> None:
        query = self.search_var.get().strip()
        self._search_results = self.store.search(query) if query else None
        self._refresh()

    def filtered_count(self) -> int:
        if self._search_results is not None:
            return len(self._search_results)
        return self.note_count()

    def add_note(self) -> None:
        text = self.add_entry.get().strip()
        if text:
            self.store.add(text=text, color=self.current_color)
            self.add_entry.delete(0, tk.END)
            self._refresh()

    def _refresh(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        notes = self._search_results if self._search_results is not None else self.store.all()
        for note in notes:
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

            pin_btn = tk.Button(frame, text="📌", width=3,
                                command=lambda nid=note.id: self.toggle_pin(nid))
            pin_btn.pack(side="right", padx=(0, 4))

            frame.pack(pady=4)

    def edit_note(self, note_id: str, new_text: str) -> None:
        self.store.update(note_id, text=new_text)
        self._refresh()

    def delete_note(self, note_id: str) -> None:
        self.store.delete(note_id)
        self._refresh()

    def toggle_pin(self, note_id: str) -> None:
        self.store.toggle_pin(note_id)
        self._refresh()

    def note_count(self) -> int:
        return len(self.store.all())

    def mainloop(self) -> None:
        self.root.mainloop()
