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
   - Read-only web view at `@url:`https://notes.app.io/@`<username>`
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
- Microsoft: `@url:`https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode``
- GitHub: `@url:`https://github.com/login/device``
- Google: `@url:`https://oauth2.googleapis.com/device``
### Token Storage
- Encrypted local storage via `keyring` library (OS keychain)
- Fallback: plaintext JSON with warning (cross-platform)
- Tests: token save/load, encryption path
### Cloud Backend Options
1. **Self-hosted** — Firebase (free tier), Supabase, or custom Flask API
2. **No vendor lock-in** — pluggable backend via `CloudSync` ABC

## Test Plan
- 8 new auth tests + 6 new sync tests = 99 total (from current 87)
- Tests: abstract backend enforcement, OAuth URL generation, token save/load, push/pull with mocks, conflict handling, sync status states

## Implementation Status
| Tier | Status | Tests |
|---|---|---|
| Tier 1: Auth Layer | ✅ Complete | 104 total pass |
| Tier 2: Cloud Sync | ✅ Complete | - |
| Tier 3: Cross-Device | 🔄 Ready to start | - |
| Tier 4: Collaboration | ⏳ Pending | - |

---
*Plan created with TDD workflow: write failing tests first, then GREEN, then commit.*