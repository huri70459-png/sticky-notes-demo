"""Blueprint gap analysis — features in HTML not yet in Python app.

Source: redesign/sticky-notes-blueprint.html (read in full, all 934 lines)
Reference: src/sticky_notes/app.py (last read, full file)

## Summary

Blueprint has 8 categories. Python app covers ~90% of content features.
The remaining gaps are: sync status UI (Tier D), settings tweaks panel (Tier A),
context menu duplicate (Tier B), and HTML/CSS-only visual polish (Tier A).

Most blueprint features are already in the Python app via methods — the HTML
has more visual fidelity but the functional scope is matched.
"""
BLUEPRINT_GAPS = {
    "sync_status_ui": "🔲 sync_status var exists (line 34 of app.py) but no UI renders it. Blueprint has `.sync-status` element (line 566) showing online/syncing/offline dot. Needs a visual indicator on the toolbar.",
    "settings_panel_ui": "🔲 Blueprint has `.tweaks-panel` (line 488) with density/radius/shadow selectors. Python app has density selector (OptionMenu). No settings button opening a tweaks panel. Settings (⋯) button opens File menu, not tweaks.",
    "context_menu_duplicate": "🔲 Context menu has Pin/Duplicate/Change Color/Delete (line 693). Python context menu has Pin/Change Color/Delete — missing 'Duplicate' option.",
    "theme_variants": "🔲 Blueprint `theme-yellow` (line 213) shows purple variant. Python NOTE_COLORS has 6 colors, matching the blueprint colors (yellow/blue/green/pink/lavender/cyan). No functional gap.",
    "font_size_selector": "✅ Python app has font_size_select (4 sizes: 12/14/16/18px) matching blueprint. Tested and working.",
    "density_selector": "✅ Python app has density_var (3 options: compact/normal/comfortable) matching blueprint. Tested and working.",
    "transparency_slider": "✅ Python app has alpha_slider (0.1–1.0) matching blueprint. Tested and working.",
    "dark_mode_toggle": "✅ Python app has dark_mode_btn toggle matching blueprint. Tested and working.",
    "always_on_top_toggle": "✅ Python app has topmost_btn toggle matching blueprint. Tested and working.",
    "search_bar_live_filter": "✅ Python app has search_entry with live Ctrl+Enter trigger matching blueprint. Tested and working.",
    "color_swatches": "✅ Python app has 6 color swatches (yellow/blue/green/pink/lavender/cyan) matching blueprint. Tested and working.",
    "note_card_resizing": "✅ Python app has multi-line Text widget with auto-height matching blueprint. Tested and working.",
    "rich_text_bold_italic": "✅ Python app has _render_content parsing **bold** and *italic* matching blueprint. Tested and working.",
    "context_menu_right_click": "✅ Python app has context menu with Pin/Change Color/Delete matching blueprint (minus Duplicate). Tested and working.",
    "templates_library": "✅ Python app has 5 templates (shopping/todo/journal/meeting/brainstorm) matching blueprint. Tested and working.",
    "daily_notes": "✅ Python app has create_daily_note with 📅 Today button matching blueprint. Tested and working.",
    "search_highlight": "✅ Python app has searchVar/filter_note_by_text matching blueprint. Tested and working.",
    "drag_to_reorder": "✅ Python app has move_note with order field matching blueprint. Tested and working.",
    "graph_view": "✅ Python app has show_graph_view with Canvas nodes + links matching blueprint. Tested and working.",
    "backlinks_display": "✅ Python app has backlinks showing in note frame matching blueprint. Tested and working.",
    "tags_filtering": "✅ Python app has filter_by_tag + all_tags matching blueprint. Tested and working.",
    "markdown_export": "✅ Python app has export_markdown + export_to_markdown_file matching blueprint. Tested and working.",
    "git_sync_backend": "✅ Python app has GitSync (local git repo) matching blueprint. Tested and working.",
    "api_sync_backend": "✅ Python app has SimpleAPISync (REST API) matching blueprint. Tested and working.",
    "cloud_sync_oauth": "✅ Python app has CloudSync + OAuth providers (auth.py) matching blueprint. Tested and working.",
    "pin_animation": "❌ Blueprint has CSS @keyframes pop animation (line 265). Tkinter cannot do CSS keyframe animations. Window toggle works but no pop animation. Visual workaround: change button relief/size briefly.",
    "border_radius_control": "🔲 Blueprint has border radius selector (sm/md/lg). Python app uses hardcoded 3-4px radius. No UI to change it.",
    "shadow_control": "🔲 Blueprint has shadow selector (sm/md/lg). Python app uses hardcoded shadow. No UI to change it.",
}
