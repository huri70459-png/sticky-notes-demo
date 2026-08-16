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
        self.always_on_top = False
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

        self.topmost_btn = tk.Button(self.form_frame, text="📌 Pin Window",
                                     command=self.toggle_topmost, width=10)
        self.topmost_btn.pack(side="right", padx=(0, 8))

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

    def toggle_topmost(self) -> None:
        """Toggle always-on-top for the entire window."""
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)
        self.topmost_btn.configure(text="📌 Pinned" if self.always_on_top else "📌 Pin Window")

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

    def _render_content(self, text_widget: tk.Text, content: str) -> None:
        """Parse simple markdown (**bold**, *italic*) and apply Tags to text_widget."""
        text_widget.tag_configure("bold", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("italic", font=("Consolas", 10, "italic"))

        # Simple state machine: iterate through content, track bold/italic spans
        plain = content.replace("**", "").replace("*", "")
        text_widget.insert("1.0", plain)

        # Find bold spans
        idx = 0
        search_text = content
        while True:
            start = search_text.find("**", idx)
            if start == -1:
                break
            end = search_text.find("**", start + 2)
            if end == -1:
                break
            inner = content[:start].replace("**", "").replace("*", "")
            inner_end = content[:end].replace("**", "").replace("*", "")
            start_pos = f"1.0+{len(inner)}c"
            end_pos = f"1.0+{len(inner_end)}c"
            text_widget.tag_add("bold", start_pos, end_pos)
            search_text = search_text[:start] + "  " + search_text[start + 2:]
            search_text = search_text[:end - 2] + "  " + search_text[end:]
            idx = end

        # Find italic spans (single asterisk)
        search_text2 = content
        idx = 0
        while True:
            start = search_text2.find("*", idx)
            if start == -1:
                break
            # Skip if this is part of **
            if start + 1 < len(search_text2) and search_text2[start + 1] == "*":
                idx = start + 2
                continue
            end = search_text2.find("*", start + 1)
            if end == -1:
                break
            inner = content[:start].replace("**", "").replace("*", "")
            inner_end = content[:end].replace("**", "").replace("*", "")
            start_pos = f"1.0+{len(inner)}c"
            end_pos = f"1.0+{len(inner_end)}c"
            text_widget.tag_add("italic", start_pos, end_pos)
            idx = end

    def _refresh(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        notes = self._search_results if self._search_results is not None else self.store.all()
        for note in notes:
            frame = tk.Frame(self.list_frame, relief="raised", bd=1)

            text_widget = tk.Text(frame, width=20, height=4, fg=note.color,
                                  font=("Consolas", 10), wrap="word")
            self._render_content(text_widget, note.content or note.text)
            text_widget.pack(side="left")

            save_btn = tk.Button(
                frame, text="Save", width=5,
                command=lambda nid=note.id, e=text_widget: self.edit_note(nid, e.get("1.0", tk.END)),
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
        self.store.update(note_id, text=new_text.rstrip("\n"))
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
