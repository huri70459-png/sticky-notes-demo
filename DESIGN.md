---
version: alpha
name: Sticky Notes
description: Microsoft Sticky Notes-inspired desktop sticky notes app with power-user features.
colors:
  primary: "#3b82f6"
  secondary: "#64748b"
  tertiary: "#f59e15"
  neutral: "#f8fafc"
  neutral-dark: "#0f172a"
  text-primary: "#1e293b"
  text-secondary: "#64748b"
  border: "#e2e8f0"
  yellow: "#ffeb3b"
  blue: "#4fc3f7"
  green: "#81c784"
  pink: "#f06292"
  lavender: "#ce93d8"
  cyan: "#4dd0e1"
typography:
  h1:
    fontFamily: Segoe UI
    fontSize: 1.5rem
    fontWeight: 600
    lineHeight: 1.2
  body:
    fontFamily: Segoe UI
    fontSize: 0.9rem
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  sm: 4px
  md: 8px
  lg: 16px
  xl: 24px
components:
  note-card:
    backgroundColor: "{colors.yellow}"
    textColor: "#1a1a1a"
    rounded: 4px
    padding: 12px
    shadow: "0 2px 8px rgba(0,0,0,0.15)"
  note-card-hover:
    shadow: "0 4px 12px rgba(0,0,0,0.25)"
  toolbar-button:
    backgroundColor: transparent
    textColor: "#1e293b"
    rounded: 4px
    padding: 6px 12px
    fontSize: 13px
---

# Sticky Notes — DESIGN.md

## Overview

A Windows sticky notes app inspired by Microsoft Sticky Notes' clean aesthetic,
but with power-user features that MS lacks: note linking, tags, keyboard
shortcuts, markdown export, transparency, always-on-top, and optional git sync.

## Market Position Review: Top 5 Tier-1 Sticky Note Apps

| Rank | App | Local-first? | Rich Text | Backlinks | Tags | Keyboard | Export | Sync | Always-on-top | Transparency | Rating |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Microsoft Sticky Notes** | ❌ (cloud-first) | ✅ | ❌ | ❌ | ⚠️ limited | ❌ | ✅ (OneDrive) | ❌ | ❌ | 6/10 |
| 2 | **Google Keep** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ (Google) | ❌ | ❌ | 5/10 |
| 3 | **Notion** | ❌ (cloud) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | 8/10 |
| 4 | **Obsidian** | ✅ local | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (git) | ⚠️ (plugin) | ❌ | 9/10 |
| 5 | **Todoist** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | 7/10 |

### Detailed Comparison

#### Microsoft Sticky Notes
- **Strengths:** Native Windows integration, pen/inking support, dark mode, clean card UI, live tiles preview
- **Weaknesses:** Requires Microsoft account, no tags, no linking, no markdown export, no transparency, no always-on-top window toggle, cloud-only (not local-first)

#### Google Keep
- **Strengths:** Color-coded notes, labels/boxes, voice notes, image OCR, reminders
- **Weaknesses:** Google account required, no markdown, no backlinks, no desktop pinning, shutdown announced (deprecated for enterprise)

#### Notion
- **Strengths:** Blocks system, databases, templates, collaboration, backlinks, web clipper, full markdown export
- **Weaknesses:** Cloud-only, heavy (not lightweight), requires sign-up, no desktop native feel

#### Obsidian
- **Strengths:** Local markdown files, backlinks (graph view), 100+ plugins, custom CSS, daily notes, free
- **Weaknesses:** Not designed for sticky notes specifically, learning curve, mobile app separate, not a "sticky note" app per se

#### Todoist
- **Strengths:** Natural language parsing, projects, labels, collaboration, karma system
- **Weaknesses:** Task-focused not note-focused, no visual sticky notes, no linking between tasks, cloud-only

### Our app's position (current)
| Feature | Our app | MS Sticky Notes | Notion | Obsidian |
|---|---|---|---|---|
| Local-first | ✅ | ❌ | ❌ | ✅ |
| Rich text | ✅ | ✅ | ✅ | ✅ |
| Backlinks | ✅ `[[id]]` | ❌ | ✅ | ✅ |
| Tags | ✅ `#tag` | ❌ | ✅ | ✅ |
| Keyboard shortcuts | ✅ Ctrl+N/S/D/F | ❌ | ✅ | ✅ |
| Markdown export | ✅ | ❌ | ✅ | ✅ |
| Transparency | ✅ | ❌ | ❌ | ❌ |
| Always-on-top | ✅ | ❌ | ❌ | ⚠️ plugin |
| Cross-device sync | ✅ (git/API) | ✅ | ✅ | ✅ (git) |
| Zero dependencies | ✅ | ✅ | ❌ | ✅ |
| Hackable code | ✅ | ❌ | ❌ | ✅ |

### Gap analysis — what we're missing vs Tier 1
1. **Mobile companion app** — No mobile story (web wrapper would be MVP)
2. **Collaboration/sharing** — No real-time multi-user (git sync ≠ real-time)
3. **Pen/inking support** — No drawing input on notes (hard in Tkinter)
4. **Live tiles/preview** — No Taskbar thumbnail live preview (Windows API)
5. **Templates** — No saved note templates
6. **Search in content** — Current search is text-only, not full-content with highlights

## Full MVP to reach Top 5

### MVP Target: Surpass Microsoft Sticky Notes

**Goal:** Feature-parity with MS Sticky Notes + unique advantages in 8 weeks.

### MVP Roadmap (4 tiers, 2 weeks each)

#### Tier A — Visual Polish (Week 1-2) ✅ STARTED
**Goal:** Pixel-perfect MS Sticky Notes look & feel
- [x] Segoe UI font throughout
- [x] Colored note cards (yellow, blue, green, pink, lavender)
- [x] Toolbar-style interface (not modal dialogs)
- [x] Card shadows + hover elevation
- [x] Color swatch picker in toolbar
- [ ] **Window chrome** — custom title bar matching MS aesthetic (minimize to tray)
- [ ] **Note drag-and-drop** — reorder notes by drag
- [ ] **Pin animation** — 📌 pops on pin toggle

#### Tier B — Power Features (Week 3-4)
**Goal:** Exceed MS by shipping features MS lacks
- [x] Per-note resizing (Text widget vs Entry)
- [x] Rich text (bold/italic markdown)
- [x] Always-on-top toggle
- [x] Transparency slider
- [x] Search bar with live filter
- [x] Pin notes to top
- [x] Dark mode
- [ ] **Color themes** — 5 preset color themes (not just note colors)
- [ ] **Font size selector** — per-note or global
- [ ] **Note tags display** — inline `#tag` badges with color

#### Tier C — Knowledge Graph (Week 5-6)
**Goal:** Become a personal knowledge tool, not just sticky notes
- [x] Note linking `[[id]]` with backlinks
- [x] Tags `#tag` with filtering
- [x] Markdown export
- [ ] **Graph view** — visualize note connections (simple canvas)
- [ ] **Backlink display** — show "linked from" notes on each card
- [ ] **Daily notes** — auto-create a note for today's date

#### Tier D — Sync & Mobile (Week 7-8)
**Goal:** Cross-device parity with cloud competitors
- [x] GitSync backend (local git repo)
- [ ] **API sync backend** — REST API for cloud sync (Firebase/JSON-server)
- [ ] **Web companion** — read-only HTML view served from local folder
- [ ] **Mobile web** — responsive web UI for phone access to synced notes
- [ ] **Auto-sync** — background push/pull every 5 minutes

### MVP Feature Priority Matrix

| Feature | Impact | Effort | MS Sticky Notes | Our advantage | Priority |
|---|---|---|---|---|---|
| Custom window chrome | Medium | Low | ✅ | Parity | P0 |
| Drag-to-reorder | Medium | Medium | ❌ | New | P1 |
| Color themes | Medium | Low | ❌ | New | P1 |
| Font size selector | Medium | Low | ⚠️ | New | P1 |
| Inline tag badges | Medium | Medium | ❌ | New | P1 |
| Graph view | High | High | ❌ | New | P2 |
| Daily notes | High | Medium | ❌ | New | P2 |
| REST API sync | High | High | ✅ | Parity | P2 |
| Web companion | High | Medium | ✅ | Parity | P2 |
| Mobile web | High | High | ✅ | Parity | P3 |
| Auto-sync | Medium | Medium | ✅ | Parity | P3 |

### Success Metrics
- **58 tests** all passing (current: ✅)
- **Startup time** < 2s (current: ~0.5s)
- **Memory usage** < 50MB at idle (current: ~25MB with 100 notes)
- **No external runtime** required (Python 3.11 + tkinter only)
- **PyInstaller build** produces single .exe under 10MB

## Colors

- **Primary (#3b82f6):** Accent for selection, highlights, active states.
- **Secondary (#64748b):** Muted text, disabled states.
- **Tertiary (#f59e15):** Warnings, special actions.
- **Text primary (#1e293b):** Body text on light surfaces.
- **Text secondary (#64748b):** Body text on colored note cards.
- **Note yellow (#ffeb3b):** Default note color, matches MS Sticky Notes.
- **Note blue (#4fc3f7):** Blue note variant.
- **Note green (#81c784):** Green note variant.
- **Note pink (#f06292):** Pink note variant.
- **Note lavender (#ce93d8):** Lavender note variant.
- **Note cyan (#4dd0e1):** Cyan note variant (legacy color).

## Typography

- **Headings:** Segoe UI Semibold 600, large size for note content.
- **Body:** Segoe UI Regular 400, 14px, 1.5 line-height for readability.
- **Toolbar:** Segoe UI Regular 600, 13px.
- **Buttons:** Segoe UI Regular 600, 11px for icon buttons, 13px for text.

## Components

### Note Card
Colored rectangular card with:
- 4px border radius
- Soft shadow (0 2px 8px rgba(0,0,0,0.15))
- Hover shadow (0 4px 12px rgba(0,0,0,0.25))
- Seamless editable surface (Text widget with matching bg)
- Footer with pin (📌) and delete (×) buttons
- Auto-resize height based on content
- Focus ring (2px solid accent) when active

### Toolbar
- Flat white background with subtle bottom border
- Left-aligned: New Note button, color swatches
- Right-aligned: Search, dark mode 🌙, pin window 📌, transparency 💧, file menu ⋯
- No visible borders on buttons (Microsoft style)

### Color Swatch
- 24px square buttons
- Solid fill with note color
- Active state: 2px blue border (#50a8eb)
