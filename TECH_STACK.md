# The Last Braincell — Tech Stack & Architecture

> Every tool in this stack is **100% free and open source**. This is a FOSS hackathon submission — zero paid services, zero credit cards, zero vendor lock-in.

---

## Overview

| Layer | Technology | License |
|---|---|---|
| Frontend | Vanilla HTML/CSS/JS + Tailwind CDN + GSAP + React (CDN, Arsenal/Leaderboard only) | MIT / Apache 2.0 |
| Backend | Flask (Python) | BSD-3 |
| Real-time Sync | Flask-SocketIO + Socket.IO client | MIT |
| Database | SQLite (local + deployed) | Public Domain |
| Deployment | Render (free tier) | Free tier, no CC |
| Tab Monitoring | Chrome Extension (webNavigation API) | Custom (open source) |
| Icons | Phosphor Icons | MIT |
| Fonts | Google Fonts (Press Start 2P, Orbitron, Rajdhani) | OFL |
| Animations | GSAP (free tier) + Framer Motion (Arsenal/Leaderboard) | GSAP Standard / MIT |

---

## Frontend

### Already in the project

| Dependency | How it's loaded | Used where |
|---|---|---|
| **Tailwind CSS** | CDN (`cdn.tailwindcss.com`) | All pages — utility classes |
| **GSAP 3.12.2** | CDN (`cdnjs.cloudflare.com`) | `index.html` — lobby animations, battle HUD transitions |
| **Phosphor Icons** | CDN (`unpkg.com/@phosphor-icons/web`) | All pages — icon set |
| **Press Start 2P** | Google Fonts | `index.html` — pixel-art UI text |
| **Orbitron + Rajdhani** | Google Fonts | Arsenal + Leaderboard — futuristic UI text |
| **React 18** | CDN (`unpkg.com/react@18`) | Arsenal + Leaderboard only (server-rendered HTML via Python) |
| **Framer Motion 10** | CDN (`unpkg.com/framer-motion@10`) | Arsenal + Leaderboard — animated components |
| **Babel Standalone** | CDN (`unpkg.com/@babel/standalone`) | Arsenal + Leaderboard — JSX transpilation in-browser |

### Architecture notes

- **`index.html`** is the main game UI — lobby, character select, battle HUD. Pure vanilla JS, no framework.
- **`lobby.html`** is a secondary lobby template. Pure vanilla JS.
- **Arsenal** (`Leader_board/arsenal.py`) and **Leaderboard** (`Leader_board/leaderboard.py`) generate full HTML pages server-side in Python and return them as `Response` objects. They embed React/Framer Motion via CDN for client-side rendering of interactive components (inventory grid, podium animations).
- **Bright mode** (`brightmode/`) contains alternate versions of `index.html` and `lobby.html` with a light theme, plus the `minimoss.gif` background.

### What to add for multiplayer

```html
<!-- Socket.IO client — add to index.html <head> -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
```

That's it. One CDN script tag. The Socket.IO client auto-connects to the Flask-SocketIO backend.

---

## Backend

### Current stack

```
Flask 3.x
├── main.py              — App entry point, routes (/, /lobby, /arsenal, /leaderboard)
├── init_db.py           — Database schema creation + sample data seeding
├── update_db.py         — Schema migration (adds columns to existing DB)
├── inspect_db.py        — Debug utility to dump DB contents
├── update_inventory.py  — Inventory data management
├── Leader_board/
│   ├── arsenal.py       — Server-rendered Arsenal UI (React via CDN)
│   └── leaderboard.py   — Server-rendered Leaderboard UI (React via CDN)
├── instance/
│   └── focus_fighter.db — SQLite database file
├── static/
│   ├── campfire_bg.gif  — Dark mode background
│   ├── minimoss.gif     — Bright mode background
│   ├── bg_gif.gif       — Arsenal background
│   └── characters/      — char1.png through char8.png (8 preset avatars)
└── templates/
    ├── index.html       — Main game UI
    └── lobby.html       — Secondary lobby template
```

### Current `main.py` routes

| Route | Purpose |
|---|---|
| `GET /` | Serves `index.html` (main game UI) |
| `GET /lobby` | Serves `lobby.html` |
| `GET /arsenal` | Server-renders Arsenal page from DB data |
| `GET /leaderboard` | Server-renders Leaderboard page from DB data |

### What to add for multiplayer

```
pip install flask-socketio
```

**Flask-SocketIO** wraps the existing Flask app with WebSocket support. Minimal change to `main.py`:

```python
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ... existing routes stay the same ...

# New: Socket events for real-time game sync
@socketio.on('join_lobby')
def handle_join(data):
    join_room(data['room_code'])
    emit('player_joined', data, room=data['room_code'])

@socketio.on('start_game')
def handle_start(data):
    emit('game_started', data, room=data['room_code'])

@socketio.on('blocked_site_visit')
def handle_offense(data):
    emit('boss_attack', data, room=data['room_code'])

# Change app.run to socketio.run
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

---

## Real-time Communication

### Why Flask-SocketIO + Socket.IO

| Requirement | Solution |
|---|---|
| Real-time sync across different devices/computers | WebSockets (persistent bidirectional connection) |
| Works with existing Flask backend | Flask-SocketIO is a drop-in wrapper |
| Room-based multiplayer (lobby codes) | Socket.IO has built-in room support (`join_room`, `leave_room`) |
| Free and open source | Flask-SocketIO: MIT, Socket.IO: MIT |
| Works on Render free tier | Yes — Render supports WebSocket connections |

### Event architecture

```
CLIENT (Browser)                    SERVER (Flask-SocketIO)
─────────────────                   ────────────────────────

emit('join_lobby')        ───►      @socketio.on('join_lobby')
                                        join_room(code)
                          ◄───      emit('player_joined', room=code)

emit('start_game')        ───►      @socketio.on('start_game')
                          ◄───      emit('game_started', room=code)

emit('timer_tick')        ───►      @socketio.on('timer_tick')
                          ◄───      emit('sync_timer', room=code)

emit('blocked_site')      ───►      @socketio.on('blocked_site')
                          ◄───      emit('boss_attack', room=code)

emit('player_died')       ───►      @socketio.on('player_died')
                          ◄───      emit('session_reset', room=code)

emit('focus_request')     ───►      @socketio.on('focus_request')
                          ◄───      emit('focus_vote', room=code)
```

### Rooms = Lobby codes

Each 6-character lobby code maps to a Socket.IO "room." All events are scoped to the room — no cross-lobby leakage. When the host ends the game, the server emits `game_over` to the entire room and cleans up.

---

## Database

### Current: SQLite

Already in the project at `instance/focus_fighter.db`.

**Current schema** (from `init_db.py`):

```sql
-- Player table
CREATE TABLE player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL,
    selected_char VARCHAR(120),
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    health INTEGER DEFAULT 100,
    attack INTEGER DEFAULT 50,
    defense INTEGER DEFAULT 50,
    speed INTEGER DEFAULT 50,
    intellect INTEGER DEFAULT 0,
    stamina INTEGER DEFAULT 0,
    focus INTEGER DEFAULT 0,
    creativity INTEGER DEFAULT 0
);

-- Inventory table
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    name VARCHAR(120) NOT NULL,
    icon VARCHAR(80) NOT NULL,
    type VARCHAR(50) NOT NULL,
    stat VARCHAR(50) NOT NULL,
    value INTEGER NOT NULL,
    rarity VARCHAR(20) NOT NULL,
    effects_json TEXT,
    FOREIGN KEY (player_id) REFERENCES player(id)
);
```

### New tables needed

```sql
-- Active game sessions
CREATE TABLE session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_code VARCHAR(6) UNIQUE NOT NULL,
    host_id INTEGER NOT NULL,
    work_duration INTEGER NOT NULL,      -- seconds
    break_duration INTEGER NOT NULL,     -- seconds
    status VARCHAR(20) DEFAULT 'lobby',  -- lobby | work | break | won | failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES player(id)
);

-- Players in a session
CREATE TABLE session_player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    health INTEGER DEFAULT 100,
    is_alive BOOLEAN DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES session(id),
    FOREIGN KEY (player_id) REFERENCES player(id)
);

-- Team-approved blocked sites
CREATE TABLE blocked_site (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    url VARCHAR(500) NOT NULL,
    approved_by TEXT DEFAULT '[]',       -- JSON array of player_ids who approved
    is_active BOOLEAN DEFAULT 0,         -- only true when all 4 approve
    FOREIGN KEY (session_id) REFERENCES session(id)
);
```

### Why SQLite for deployment too

- SQLite works perfectly on Render's free tier (file-based, no external DB service needed).
- The DB file lives on the server's ephemeral filesystem. For a hackathon demo, this is fine.
- If persistence across deploys is needed later, Render supports free PostgreSQL (still FOSS), but SQLite is simpler for now.

---

## Deployment

### Platform: Render (free tier)

| Feature | Render Free Tier |
|---|---|
| Cost | $0, no credit card required |
| Flask support | Native (Python runtime) |
| WebSocket support | Yes (required for Flask-SocketIO) |
| Custom domain | Optional (free `.onrender.com` subdomain) |
| Auto-deploy from GitHub | Yes |
| Sleep after inactivity | Yes (spins down after 15 min, cold start ~30s) |

### Deployment files needed

**`requirements.txt`** (create at project root):
```
flask
flask-socketio
gunicorn
eventlet
```

**`render.yaml`** (optional, for one-click deploy):
```yaml
services:
  - type: web
    name: the-last-braincell
    runtime: python
    buildCommand: pip install -r requirements.txt && python init_db.py
    startCommand: gunicorn --worker-class eventlet -w 1 main:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Deploy steps

1. Push code to GitHub.
2. Go to [render.com](https://render.com) → New Web Service → connect the repo.
3. Set build command: `pip install -r requirements.txt && python init_db.py`
4. Set start command: `gunicorn --worker-class eventlet -w 1 main:app --bind 0.0.0.0:$PORT`
5. Deploy. Live URL is generated automatically.

### Alternative: Railway (free tier)

Railway also works (free $5/month credit, no CC). Same setup as Render. Use whichever deploys faster tonight.

---

## Browser Extension (Tab Monitoring)

### Purpose

Detect when a player visits a blocked website during a work phase. This **cannot** be done from a regular web page — browsers don't allow websites to see what other tabs are open. A lightweight Chrome extension is required.

### Architecture

```
Chrome Extension (Manifest V3)
├── manifest.json        — Permissions: webNavigation, storage, tabs
├── background.js        — Service worker: listens for tab URL changes
├── popup.html           — Simple UI: connect to game session
└── popup.js             — Handles session connection
```

### How it works

1. Player installs the extension (unpacked, from source — no Chrome Web Store needed).
2. Extension connects to the Flask-SocketIO server via the Socket.IO client.
3. `background.js` listens to `chrome.webNavigation.onCompleted` — fires whenever any tab finishes loading a URL.
4. On each navigation event, the extension checks the URL against the blocked list (synced from the server).
5. If the URL matches a blocked site and the game is in a work phase → the extension emits a `blocked_site_visit` event to the server.
6. The server broadcasts a `boss_attack` event to all players in the room.

### Key API

```javascript
// background.js (service worker)
chrome.webNavigation.onCompleted.addListener((details) => {
    if (details.frameId !== 0) return; // main frame only
    const url = new URL(details.url);
    if (blockedDomains.includes(url.hostname)) {
        socket.emit('blocked_site_visit', {
            room_code: currentRoom,
            player_id: playerId,
            url: url.hostname
        });
    }
});
```

### Permissions required

```json
{
    "manifest_version": 3,
    "name": "The Last Braincell — Focus Guard",
    "version": "1.0",
    "permissions": ["webNavigation", "storage", "tabs"],
    "host_permissions": ["<all_urls>"],
    "background": {
        "service_worker": "background.js"
    },
    "action": {
        "default_popup": "popup.html"
    }
}
```

### Why this is FOSS

- Uses only standard Chrome Extension APIs (Manifest V3, fully open).
- No third-party SDKs or paid monitoring services.
- The extension source code ships with the repo — users load it unpacked via `chrome://extensions`.

---

## Why Everything is FOSS

| Component | License | Verification |
|---|---|---|
| **Python** | PSF License (OSI-approved) | [python.org/psf](https://www.python.org/psf/) |
| **Flask** | BSD-3-Clause | [github.com/pallets/flask](https://github.com/pallets/flask/blob/main/LICENSE.txt) |
| **Flask-SocketIO** | MIT | [github.com/miguelgrinberg/Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) |
| **Socket.IO (client)** | MIT | [github.com/socketio/socket.io-client](https://github.com/socketio/socket.io-client) |
| **SQLite** | Public Domain | [sqlite.org/copyright.html](https://www.sqlite.org/copyright.html) |
| **Tailwind CSS** | MIT | [github.com/tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss/blob/master/LICENSE) |
| **GSAP (free tier)** | Standard License (free for non-commercial) | [gsap.com/community/standard-license](https://gsap.com/community/standard-license/) |
| **Phosphor Icons** | MIT | [github.com/phosphor-icons/core](https://github.com/phosphor-icons/core/blob/main/LICENSE) |
| **React** | MIT | [github.com/facebook/react](https://github.com/facebook/react/blob/main/LICENSE) |
| **Framer Motion** | MIT | [github.com/framer/motion](https://github.com/framer/motion/blob/main/LICENSE.md) |
| **Google Fonts** | SIL Open Font License | [fonts.google.com](https://fonts.google.com/attribution) |
| **Gunicorn** | MIT | [github.com/benoitc/gunicorn](https://github.com/benoitc/gunicorn/blob/master/LICENSE) |
| **Eventlet** | MIT | [github.com/eventlet/eventlet](https://github.com/eventlet/eventlet/blob/master/LICENSE) |
| **Render** | Free tier (no payment) | [render.com/pricing](https://render.com/pricing) |
| **Chrome Extension APIs** | Open standard (Chromium) | [developer.chrome.com](https://developer.chrome.com/docs/extensions/) |

**No paid APIs. No proprietary SDKs. No credit card required anywhere.**

---

## Setup Instructions

### Run locally

```bash
# 1. Clone the repo
git clone https://github.com/sadhana-2008/Focus_Fighter.git
cd Focus_Fighter

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install flask flask-socketio eventlet

# 5. Initialize the database
python init_db.py

# 6. Run the app
python main.py

# 7. Open in browser
# http://127.0.0.1:5000
```

### Install the Chrome extension (for tab monitoring)

```bash
# 1. Open Chrome → chrome://extensions
# 2. Enable "Developer mode" (top right toggle)
# 3. Click "Load unpacked"
# 4. Select the extension/ folder from the project root
# 5. The extension icon appears in the toolbar — click it to connect to your game session
```

### Deploy to Render

```bash
# 1. Create requirements.txt at project root
echo "flask\nflask-socketio\ngunicorn\neventlet" > requirements.txt

# 2. Push to GitHub
git add .
git commit -m "Add deployment config"
git push

# 3. Go to render.com → New Web Service → Connect GitHub repo
# 4. Set:
#    Build command:  pip install -r requirements.txt && python init_db.py
#    Start command:  gunicorn --worker-class eventlet -w 1 main:app --bind 0.0.0.0:$PORT
# 5. Click Deploy → wait ~2 minutes → live URL ready
```

### Deploy to Railway (alternative)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login + deploy
railway login
railway init
railway up

# Railway auto-detects Python + requirements.txt
```
