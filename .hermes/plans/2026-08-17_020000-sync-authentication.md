# Plan: Account-Based Cross-Device Sync

## Goal
Add login (Microsoft/GitHub/Google) + cloud sync so users can access notes on any PC.
Extends Tier D from the blueprint with authentication and real-time sync.

## Trigger
`/plan sync-authentication`

## Background
Current app supports: GitSync (local git repo), SimpleAPISync (REST API). 
Missing: user authentication, cloud backend, cross-device access.

## Approach (TDD — RED → GREEN → COMMIT)

### Tier 1: Authentication Layer (Week 1)
1. **Auth backend abstraction**
   - `AuthBackend` ABC (login, logout, get_token, is_authenticated)
   - Tests: abstract class enforcement, token persistence
2. **OAuth providers**
   - `MicrosoftAuth`, `GitHubAuth`, `GoogleAuth` subclasses
   - Use `requests` + OAuth2 device flow (desktop app)
   - Tests: provider creation, login URL generation, token storage
3. **Auth UI**
   - Login button in toolbar → opens auth menu
   - User avatar/name display when logged in
   - Logout button
   - Tests: auth button exists, login state tracking

### Tier 2: Cloud Sync Backend (Week 2)
1. **CloudSync backend**
   - Extends `SyncBackend` ABC
   - `push()`: POST notes to `/api/notes/sync` with auth token
   - `pull()`: GET notes from `/api/notes/sync`
   - Conflict resolution: last-write-wins with timestamp
   - Tests: push/pull with mock HTTP, conflict handling
2. **Sync status UI**
   - Sync indicator: 🔵 online, 🟡 syncing, 🔴 disconnected
   - Auto-sync toggle (5min interval)
   - Click-to-sync button
   - Tests: status states, auto-sync scheduling

### Tier 3: Cross-Device Access (Week 3)
1. **Web companion**
   - Read-only web view at `https://notes.app.io/@<username>`
   - Served via Flask (optional dependency) or static export
   - Tests: web route exists, read-only rendering
2. **Mobile web**
   - Responsive CSS for mobile browsers
   - Tests: mobile viewport meta tag
3. **Auto-sync background task**
   - `cronjob`-style timer (Tk `after()` for desktop)
   - 5-minute interval, configurable
   - Tests: timer scheduling, sync trigger

### Tier 4: Real-Time Collaboration (Week 4)
1. **WebSocket integration**
   - `CollaborativeSync` using `websockets` library
   - Presence indicators (user dots on notes)
   - Comment threads on notes
   - Tests: presence detection, concurrent edit merge

## Technical Decisions

### OAuth Flow
- **Device Flow** (not web server flow) — desktop app, no local server needed
- Microsoft: `https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode`
- GitHub: `https://github.com/login/device`
- Google: `https://oauth2.googleapis.com/device`

### Token Storage
- Encrypted local storage via `keyring` library (OS keychain)
- Fallback: plaintext JSON with warning (cross-platform)
- Tests: token save/load, encryption path

### Cloud Backend Options
1. **Self-hosted** — Firebase (free tier), Supabase, or custom Flask API
2. **No vendor lock-in** — pluggable backend via `CloudSync` ABC
3. **Sync format** — JSON over REST API, same Note serialization

### Sync Protocol
```
POST /api/notes/sync
Headers: Authorization: Bearer <token>
Body: {"notes": [...full note list...], "timestamp": <unix>}

GET /api/notes/sync
Headers: Authorization: Bearer <token>
Response: {"notes": [...remote notes...], "timestamp": <unix>}
```

Conflict resolution: compare `updated_at` timestamp on each note, newer wins.

## Files to Create/Modify
- `src/sticky_notes/auth.py` — NEW: AuthBackend ABC + provider implementations
- `src/sticky_notes/sync.py` — ADD: CloudSync class
- `src/sticky_notes/app.py` — ADD: auth menu, sync status UI, auto-sync timer
- `tests/test_auth.py` — NEW: 8 tests for auth layer
- `tests/test_app_interactive.py` — ADD: 6 tests for cloud sync + auth UI
- `requirements.txt` — ADD: `requests`, `keyring` (optional)

## Risk & Mitigation
- **Risk:** OAuth device flow requires browser visit — friction
  - **Mitigation:** Cache token, only login once
- **Risk:** `keyring` not available on all platforms
  - **Mitigation:** Fallback to plaintext with warning, stdlib only core
- **Risk:** Real-time collaboration needs WebSocket server
  - **Mitigation:** Start with polling sync, WebSocket as Tier D stretch goal

## Dependencies
- `requests` (HTTP client, stdlib fallback to urllib)
- `keyring` (optional, for secure token storage)
- `websockets` (optional, Tier 4 only)

## Acceptance Criteria
- 8 new auth tests + 6 new sync tests = 99 total tests passing
- Login with Microsoft/GitHub/Google via device flow
- Notes sync to cloud and accessible on another PC
- Works without internet (local-first, sync when online)
- No external dependency required for core functionality
