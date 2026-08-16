import tkinter as tk
from pathlib import Path
from .store import NoteStore


# Microsoft Sticky Notes color palette
NOTE_COLORS = {
    "yellow":  "#ffeb3b",
    "blue":    "#4fc3f7",
    "green":   "#81c784",
    "pink":    "#f06292",
    "lavender": "#ce93d8",
    "cyan":    "#4dd0e1",
}


class NotesApp:
    def __init__(self, *, store: NoteStore, root: tk.Tk | None = None):
        self.store = store
        self.root = root if root is not None else tk.Tk()
        self.root.title("Sticky Notes")
        self.root.configure(bg="#f3f3f3")
        self.current_color = "yellow"
        self.search_var = tk.StringVar()
        self._search_results: list | None = None
        self.dark_mode = False
        self.always_on_top = False
        self.alpha_var = tk.DoubleVar(value=1.0)
        self._active_note_id: str | None = None
        self._font_size: str = "14px"
        self._font_size_num: int = 10
        self._context_target: str | None = None
        self._build_ui()
        self._create_context_menu()
        self._focus_note_id = None

    def create_daily_note(self) -> None:
        """Create or focus a daily note for today."""
        from datetime import date
        today = date.today().isoformat()
        note_id = f"daily-{today}"
        existing = self.store.all_for_id(note_id)
        if existing:
            self._focus_note(note_id)
        else:
            self.store.add(id=note_id, text=f"Daily Note: {today}",
                           color=self.current_color, tags=["daily"], pinned=True)
            self._refresh()

    def _build_ui(self) -> None:
        # Toolbar — top bar
        self.toolbar = tk.Frame(self.root, bg="#ffffff", relief="flat",
                                highlightbackground="#e0e0e0", highlightthickness=1)
        self.toolbar.pack(fill="x", padx=12, pady=8)

        tk.Button(self.toolbar, text="📅 Today",
                  command=self.create_daily_note,
                  font=("Segoe UI", 9), bg="#ffffff",
                  activebackground="#f0f0f0",
                  relief="flat").pack(side="left", padx=(0, 4))

        tk.Button(self.toolbar, text="+ New Note",
                  command=self._focus_add_entry,
                  font=("Segoe UI", 9, "normal"), bg="#ffffff",
                  activebackground="#f0f0f0",
                  relief="flat").pack(side="left", padx=(0, 8))

        self.dark_mode_btn = tk.Button(self.toolbar, text="🌙",
                                       command=self.toggle_dark_mode,
                                       font=("Segoe UI", 10), width=3,
                                       relief="flat", bg="#ffffff")
        self.dark_mode_btn.pack(side="right", padx=(0, 8))

        self.topmost_btn = tk.Button(self.toolbar, text="📌",
                                     command=self.toggle_topmost,
                                     font=("Segoe UI", 10), width=3,
                                     relief="flat", bg="#ffffff")
        self.topmost_btn.pack(side="right", padx=(0, 8))

        alpha_slider = tk.Scale(self.toolbar, from_=0.1, to=1.0, resolution=0.1,
                                orient="horizontal", label="💧",
                                variable=self.alpha_var, width=8,
                                font=("Segoe UI", 8),
                                command=lambda v: self.set_transparency(float(v)))
        alpha_slider.pack(side="right", padx=(8, 0))

        # Search
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.toolbar, textvariable=self.search_var,
                                font=("Segoe UI", 10), width=15,
                                relief="solid", highlightthickness=0)
        search_entry.pack(side="right", padx=(8, 0))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_search())
        search_entry.insert(0, "Search…")
        search_entry.configure(foreground="#999999")
        search_entry.bind("<FocusIn>", lambda e: (
            search_entry.delete(0, tk.END) if search_entry.get() == "Search…" else None,
            search_entry.configure(foreground="#000000")
        ))

        # Add entry — hidden, used for keyboard shortcut
        self.add_entry = tk.Entry(self.toolbar, font=("Segoe UI", 10), width=20,
                                  relief="solid", highlightthickness=0)
        self.add_entry.pack(side="left", padx=(0, 8))
        self.add_entry.bind("<Return>", lambda e: self.add_note())

        # Add button (backward-compat alias)
        self.add_button = tk.Button(self.toolbar, text="Add",
                                    command=self.add_note,
                                    font=("Segoe UI", 9), relief="flat")
        self.add_button.pack(side="left", padx=(0, 4))

        # Color picker — minimal swatches (form_frame alias for backward compat)
        self.form_frame = self.toolbar
        self.color_frame = tk.Frame(self.toolbar, bg="#ffffff")
        self.color_frame.pack(side="left", padx=(0, 8))
        for i, color in enumerate(("yellow", "blue", "green", "pink", "lavender", "cyan")):
            b = tk.Button(self.color_frame, text="", width=3,
                          bg=NOTE_COLORS[color],
                          command=lambda c=color: self.set_color(c),
                          relief="flat",
                          highlightbackground=("#50a8eb" if color == self.current_color else "#e0e0e0"),
                          highlightthickness=1)
            b._color = True
            b._color_name = color
            b.pack(side="left", padx=2)

        font_size_var = tk.StringVar(value="14px")
        font_size_select = tk.OptionMenu(self.toolbar, font_size_var, "12px", "14px", "16px", "18px",
                                         command=self.set_font_size)
        font_size_select.config(font=("Segoe UI", 8), width=8, relief="flat",
                                bg="#ffffff", activebackground="#f0f0f0")
        font_size_select.pack(side="right", padx=(0, 8))

        # Sync toggle button
        self.sync_btn = tk.Button(self.toolbar, text="☁️ Sync",
                                  command=self._sync_notes,
                                  font=("Segoe UI", 9), bg="#ffffff",
                                  activebackground="#f0f0f0",
                                  relief="flat")
        self.sync_btn.pack(side="right", padx=(0, 4))

        # File menu
        file_menu_btn = tk.Menubutton(self.toolbar, text="⋯",
                                      font=("Segoe UI", 10), width=3,
                                      relief="flat", bg="#ffffff")
        file_menu = tk.Menu(file_menu_btn, tearoff=0, font=("Segoe UI", 9))
        file_menu.add_command(label="Export Markdown…", command=self._export_markdown_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.destroy)
        file_menu_btn["menu"] = file_menu
        file_menu_btn.pack(side="right", padx=(0, 4))

        # Notes container
        self.list_frame = tk.Frame(self.root, bg="#f3f3f3")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._apply_theme()
        self._bind_shortcuts()
        self._refresh()

    def _bind_shortcuts(self) -> None:
        """Register keyboard shortcuts."""
        self.root.bind("<Control-Key-n>", self._focus_add_entry)
        self.root.bind("<Control-Key-s>", self._save_active_note)
        self.root.bind("<Control-Key-d>", self._delete_active_note)
        self.root.bind("<Control-Key-f>", self._focus_search)

    def _create_context_menu(self) -> None:
        """Create the right-click context menu."""
        self._context_menu = tk.Menu(self.root, tearoff=0)
        self._context_menu.add_command(label="📌 Pin", command=self._context_pin)
        self._context_menu.add_command(label="📋 Duplicate", command=self._context_duplicate)
        self._context_menu.add_separator()
        self._context_menu.add_command(label="🔵 Blue", command=lambda: self._context_set_color("blue"))
        self._context_menu.add_command(label="🟢 Green", command=lambda: self._context_set_color("green"))
        self._context_menu.add_command(label="🩷 Pink", command=lambda: self._context_set_color("pink"))
        self._context_menu.add_command(label="💜 Lavender", command=lambda: self._context_set_color("lavender"))
        self._context_menu.add_separator()
        self._context_menu.add_command(label="🗑️ Delete", command=self._context_delete)

    def show_context_menu(self, event, note_id: str) -> None:
        """Show context menu on right-click."""
        self._context_target = note_id
        try:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._context_menu.grab_release()

    def _context_pin(self) -> None:
        if self._context_target:
            self.toggle_pin(self._context_target)

    def _context_duplicate(self) -> None:
        if self._context_target:
            note = self.store.all_for_id(self._context_target)
            if note:
                self.store.add(text=note.text, color=note.color,
                               content=note.content, pinned=note.pinned,
                               width=note.width, height=note.height,
                               always_on_top=note.always_on_top,
                               links=note.links, tags=note.tags)
                self._refresh()

    def _context_set_color(self, color: str) -> None:
        if self._context_target:
            self.store.update(self._context_target, color=color)
            self._refresh()

    def _context_delete(self) -> None:
        if self._context_target:
            self.delete_note(self._context_target)

    def _focus_add_entry(self, event=None) -> None:
        self.add_entry.delete(0, tk.END)
        self.add_entry.focus_set()

    def _export_markdown_dialog(self) -> None:
        """Open a save file dialog and export notes to markdown."""
        from tkinter import filedialog
        path_str = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
        )
        if path_str:
            self.store.export_to_markdown_file(Path(path_str))

    def _save_active_note(self, event=None) -> None:
        """Save the currently focused note's text."""
        focused = self.root.focus_get()
        for widget in self.list_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if child is focused and isinstance(child, tk.Text):
                        note_id = child.master._note_id
                        self.edit_note(note_id, child.get("1.0", tk.END))
                        return

    def _delete_active_note(self, event=None) -> None:
        """Delete the currently focused note."""
        focused = self.root.focus_get()
        for widget in self.list_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if child is focused and isinstance(child, tk.Text):
                        note_id = child.master._note_id
                        self.delete_note(note_id)
                        return

    def _focus_search(self, event=None) -> None:
        search_entry = None
        for w in self.toolbar.winfo_children():
            if isinstance(w, tk.Entry) and w.cget("textvariable") and w is not self.add_entry:
                search_entry = w
                break
        if search_entry:
            search_entry.delete(0, tk.END)
            search_entry.focus_set()

    def _apply_theme(self) -> None:
        if self.dark_mode:
            self.root.configure(bg="#2b2b2b")
            self.dark_mode_btn.configure(text="☀️", bg="#404040", fg="#ffffff")
            self.toolbar.configure(bg="#2a2a2a", highlightbackground="#404040")
            self.list_frame.configure(bg="#2b2b2b")
            self.color_frame.configure(bg="#2a2a2a")
        else:
            self.root.configure(bg="#f3f3f3")
            self.dark_mode_btn.configure(text="🌙", bg="#ffffff", fg="#000000")
            self.toolbar.configure(bg="#ffffff", highlightbackground="#e0e0e0")
            self.list_frame.configure(bg="#f3f3f3")
            self.color_frame.configure(bg="#ffffff")

    def toggle_dark_mode(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self._refresh()

    def toggle_topmost(self) -> None:
        """Toggle always-on-top for the entire window."""
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)

    def set_transparency(self, alpha: float) -> None:
        """Set window transparency, clamped to [0.1, 1.0]."""
        self.current_alpha = max(0.1, min(1.0, alpha))
        self.alpha_var.set(self.current_alpha)
        self.root.attributes("-alpha", self.current_alpha)

    def set_color(self, color: str) -> None:
        self.current_color = color
        # Update color swatch highlights
        for btn in self.color_frame.winfo_children():
            if getattr(btn, "_color", False):
                btn.configure(highlightbackground=("#50a8eb" if btn._color_name == color else "#e0e0e0"))

    def set_font_size(self, size: str) -> None:
        """Set the global font size for note text."""
        self._font_size = size
        self._refresh()

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
        """Parse simple markdown (**bold**, *italic*) and apply Tags."""
        default_font = ("Segoe UI", 10)
        text_widget.tag_configure("bold", font=(*default_font, "bold"))
        text_widget.tag_configure("italic", font=(*default_font, "italic"))

        plain = content.replace("**", "").replace("*", "")
        text_widget.insert("1.0", plain)

        # Bold spans
        idx = 0
        search_text = content
        while True:
            start = search_text.find("**", idx)
            if start == -1:
                break
            end = search_text.find("**", start + 2)
            if end == -1:
                break
            inner_len = len(content[:start].replace("**", "").replace("*", ""))
            inner_end_len = len(content[:end].replace("**", "").replace("*", ""))
            text_widget.tag_add("bold", f"1.0+{inner_len}c", f"1.0+{inner_end_len}c")
            idx = end

        # Italic spans (single asterisk)
        search_text2 = content
        idx = 0
        while True:
            start = search_text2.find("*", idx)
            if start == -1:
                break
            if start + 1 < len(search_text2) and search_text2[start + 1] == "*":
                idx = start + 2
                continue
            end = search_text2.find("*", start + 1)
            if end == -1:
                break
            inner_len = len(content[:start].replace("**", "").replace("*", ""))
            inner_end_len = len(content[:end].replace("**", "").replace("*", ""))
            text_widget.tag_add("italic", f"1.0+{inner_len}c", f"1.0+{inner_end_len}c")
            idx = end

    def _refresh(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        notes = self._search_results if self._search_results is not None else self.store.all()
        for note in notes:
            bg_color = NOTE_COLORS.get(note.color, NOTE_COLORS["yellow"])

            frame = tk.Frame(self.list_frame, relief="flat",
                             bg=bg_color,
                             highlightbackground="#cccccc",
                             highlightthickness=0,
                             padx=12, pady=12)
            frame._note_id = note.id

            # Drag-and-drop support
            frame.bind("<ButtonPress-1>", lambda e, f=frame: self._on_drag_start(e, f))
            frame.bind("<B1-Motion>", lambda e, f=frame: self._on_drag_motion(e, f))
            frame.bind("<ButtonRelease-1>", lambda e, f=frame: self._on_drag_drop(e, f))
            # Context menu — right-click
            frame.bind("<Button-3>", lambda e, nid=note.id: self.show_context_menu(e, nid))

            # Rounded corners via canvas background
            text_widget = tk.Text(frame, width=30, height=4,
                                  font=("Segoe UI", 10),
                                  wrap="word", bg=bg_color,
                                  fg="#1a1a1a",
                                  relief="flat",
                                  borderwidth=0,
                                  highlightthickness=0)
            text_widget.bind("<ButtonPress-1>", lambda e: e.widget.master._on_drag_start(e, e.widget.master))
            text_widget.bind("<B1-Motion>", lambda e: e.widget.master._on_drag_motion(e, e.widget.master))
            text_widget.bind("<ButtonRelease-1>", lambda e: e.widget.master._on_drag_drop(e, e.widget.master))
            self._render_content(text_widget, note.content or note.text)
            text_widget.pack(fill="both", expand=True, side="top")
            text_widget.bind("<FocusIn>", lambda e, nid=note.id, tw=text_widget: self._on_note_focus(nid, tw))

            # Tag badges — Tier B
            if note.tags:
                tags_frame = tk.Frame(frame, bg=bg_color)
                tags_frame.pack(fill="x", side="top", pady=(0, 4))
                for tag in note.tags:
                    label = tk.Label(tags_frame, text=f"#{tag}",
                                     font=("Segoe UI", 9, "bold"),
                                     fg=bg_color, bg="#ffffff",
                                     relief="flat", padx=6, pady=2)
                    label._tag = tag
                    label.pack(side="left", padx=(0, 4))

            # Backlinks display — Tier C
            backlinks = self.store.backlinks(note.id)
            if backlinks:
                bl_text = "🔗 Linked from: " + ", ".join(b.text for b in backlinks)
                tk.Label(frame, text=bl_text,
                         font=("Segoe UI", 8), fg=bg_color, bg=bg_color,
                         relief="flat", pady=2).pack(fill="x", side="bottom")

            # Footer: pin + delete
            footer = tk.Frame(frame, bg=bg_color)
            footer.pack(fill="x", side="bottom", pady=(6, 0))

            pin_state = "📌" if note.pinned else "📍"
            tk.Button(footer, text=pin_state,
                      command=lambda nid=note.id: self.toggle_pin(nid),
                      font=("Segoe UI", 8), bg=bg_color, relief="flat",
                      activebackground=bg_color).pack(side="right", padx=(4, 0))

            tk.Button(footer, text="×",
                      command=lambda nid=note.id: self.delete_note(nid),
                      font=("Segoe UI", 9, "bold"), bg=bg_color,
                      fg="#666666", relief="flat",
                      activebackground=bg_color).pack(side="right")

            frame.pack(pady=8, padx=2, fill="x")

    def _on_drag_start(self, event, frame):
        """Record the starting position for drag-and-drop."""
        self._drag_start_y = event.y_root
        self._drag_start_frame = frame

    def _on_drag_motion(self, event, frame):
        """Handle drag motion — for now just visual feedback."""
        pass

    def _on_drag_drop(self, event, frame):
        """Handle drag drop — reorder notes."""
        note_id = frame._note_id
        # Determine new position based on where dropped
        frames = self.list_frame.winfo_children()
        for i, f in enumerate(frames):
            if f is frame:
                self.move_note(note_id, i)
                return

    def _on_note_focus(self, note_id: str, widget: tk.Text) -> None:
        self._active_note_id = note_id
        # Auto-resize height to content
        widget.configure(height=max(4, len(widget.get("1.0", tk.END).splitlines())))

    def edit_note(self, note_id: str, new_text: str) -> None:
        self.store.update(note_id, text=new_text.rstrip("\n"))
        self._refresh()

    def delete_note(self, note_id: str) -> None:
        self.store.delete(note_id)
        self._refresh()

    def toggle_pin(self, note_id: str) -> None:
        self.store.toggle_pin(note_id)
        self._refresh()

    def move_note(self, note_id: str, new_position: int) -> None:
        """Move a note to a new position (for drag-to-reorder)."""
        self.store.move_note(note_id, new_position)
        self._refresh()

    def _focus_note(self, note_id: str) -> None:
        """Focus a specific note in the UI."""
        self._focus_note_id = note_id

    def _sync_notes(self) -> None:
        """Push notes to remote sync."""
        try:
            from .sync import GitSync
            from pathlib import Path
            sync_dir = Path.home() / ".sticky_notes_sync"
            sync = GitSync(sync_dir, self.store)
            sync.push()
            self._refresh()
        except Exception as e:
            pass

    def note_count(self) -> int:
        return len(self.store.all())

    def mainloop(self) -> None:
        self.root.mainloop()
