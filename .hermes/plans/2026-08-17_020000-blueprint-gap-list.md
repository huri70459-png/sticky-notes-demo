# Sticky Notes — Blueprint Implementation Tracker

Last updated: 2026-08-17 based on `redesign/sticky-notes-blueprint.html` + `src/sticky_notes/app.py`

## Status Legend
- ✅ Done (tests passing)
- 🔲 Not started
- 💡 Planned / blocked (platform limitation)
- 🏗️ In progress

---

## Section 1: Complete Implementation Gap Report

### ✅ Tier A — Visual Polish (ALL DONE)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| Custom window chrome | `.window-chrome` (line 70) | ✅ Done | Minimize/maximize/close buttons + title bar |
| Toolbar-style UI | `.toolbar` (line 112) | ✅ Done | Flatter buttons, segmented controls |
| Colored note cards (6 colors) | `NOTE_COLORS` (line 7) | ✅ Done | yellow/blue/green/pink/lavender/cyan |
| Card shadows + hover elevation | `:root --shadow-*` (line 21) | ✅ Done | shadow-sm/md/lg applied |
| Color swatch picker in toolbar | `.theme-selector` (line 187) | ✅ Done | 6 swatches, active state |
| Font size selector | `.font-size-selector` (line 220) | ✅ Done | 12/14/16/18px |
| Transparency slider | `.transparency-slider` (line 319) | ✅ Done | 0.1–1.0 |
| Dark mode toggle | `.toggle-switch` (line 286) | ✅ Done | 🌙→☀️ |
| Always-on-top toggle | `.topmost-btn` (line 324) | ✅ Done | 📌 |
| Search bar with live filter | `.search-container` (line 156) | ✅ Done | Ctrl+F |
| Per-note resizing (Text widget) | `.note textarea` (line 395) | ✅ Done | Auto-height |
| Rich text (bold/italic markdown) | `.note .bold/italic` (line 411) | ✅ Done | **bold**, *italic* |

### ✅ Tier B — Power Features (ALL DONE)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| Note tags display | `.tag-badge` (line 249) | ✅ Done | #tag parsed from text |
| Context menu (right-click) | `contextmenu` event (line 744) | ✅ Done | Pin/Duplicate/Color/Delete |
| Templates library | `templates` (line 40) | ✅ Done | shopping/todo/journal/meeting/brainstorm |
| Per-note sorting (order field) | N/A | ✅ Done | order on Note, move_note |
| Inline tag badges | `.tag-badge` (line 249) | ✅ Done | Under note text |

### ✅ Tier C — Knowledge Graph (ALL DONE)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| Note linking [[id]] + backlinks | N/A | ✅ Done | _LINK_RE, backlinks(), backlink Labels |
| Tags + filtering | N/A | ✅ Done | _TAG_RE, filter_by_tag |
| Markdown export | N/A | ✅ Done | export_markdown() |
| Graph view | `.graph-view` (line 277) | ✅ Done | show_graph_view() canvas |
| Backlink display | `.backlinks` (line 305) | ✅ Done | "🔗 Linked from:" |
| Daily notes | `.daily-note-btn` (line 315) | ✅ Done | 📅 Today |
| AI suggestions | suggest_tags/suggest_links | ✅ Done | Methods in app.py |

### ✅ Tier D — Sync (PARTIALLY DONE)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| GitSync backend | N/A | ✅ Done | sync.py |
| REST API sync backend | N/A | ✅ Done | SimpleAPISync in sync.py |
| CloudSync (OAuth-based) | N/A | 🔲 Pending | Not started |
| Auth backends (Microsoft/GitHub/Google) | N/A | ✅ Done | auth.py |
| Web companion (read-only HTML) | N/A | 🔲 Pending | Static HTML export from notes |
| Mobile web (responsive UI) | N/A | 🔲 Pending | Depends on web companion |
| Auto-sync (background timer) | N/A | 🔲 Pending | Tk after() loop, 5-min |

### 🔲 Tier E — Collaboration (NOT STARTED)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| Real-time collaboration | N/A | 🔲 Pending | WebSocket-based, CollaborativeSync ABC |
| Presence indicators (user dots) | N/A | 🔲 Pending | Per-user colored dot |
| Comment threads on notes | N/A | 🔲 Pending | Per-note comments list |
| Permission levels | N/A | 🔲 Pending | Read/write/comment access |

### 💡 Blocked (Platform Limitations)
| Feature | Blueprint ref | Status | Notes |
|---|---|---|---|
| Pen/inking support | N/A | 💡 Blocked | Tkinter lacks freehand drawing |
| Live preview thumbnails | N/A | 💡 Blocked | Windows API ITaskbarList3 not in stdlib |

---

## Section 2: Todo List

```yaml
---
merge: false
todos:
  - id: cloud_sync_backend
    content: Wire CloudSync backend to OAuth + REST API with conflict resolution
    status: pending
  - id: auth_ui_integration
    content: Login/logout buttons + user display in toolbar
    status: pending
  - id: sync_status_ui
    content: Sync indicator (🔵🟡🔴) + auto-sync toggle + click-to-sync
    status: pending
  - id: auto_sync_background
    content: Tk after() timer for periodic 5-min sync
    status: pending
  - id: settings_panel_ui
    content: Tweaks panel (density/radius/shadow options) via settings (⋯) button
    status: pending
  - id: ai_suggestions_popup
    content: Hover note → AI suggestions panel with clickable apply chips
    status: pending
---
```

---

## Section 3: Quick Validation

```bash
# Current test count
.venv/Scripts/python -m pytest tests/ -q --tb=short
# Expected: 87 passed (baseline before new work)
```
