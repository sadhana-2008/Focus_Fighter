import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_from_directory, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import sqlite3
import json
import socket
import shutil
import string
import random
from Leader_board.arsenal import Character, Item, render_arsenal
from Leader_board.leaderboard import render_leaderboard

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the-last-braincell-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# ─────────────────────────────────────────────
# IN-MEMORY LOBBY STATE
# ─────────────────────────────────────────────
# Structure: lobbies[room_code] = {
#     "host_sid": str,
#     "players": { sid: { "name", "avatar", "health", "xp", "is_alive" } },
#     "phase": "lobby" | "work" | "break" | "won" | "failed",
#     "work_duration": int (seconds),
#     "break_duration": int (seconds),
#     "timer_remaining": int (seconds),
#     "blocked_sites": [ { "url": str, "approved_by": [sid, ...], "is_active": bool } ],
#     "focus_requests": { sid: { "duration": int, "approved_by": [sid, ...] } }
# }
lobbies = {}

# Map socket SIDs to their room code for disconnect handling
sid_to_room = {}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def generate_room_code():
    """Generate a unique 6-character lobby code (e.g. 'A3X-K9')."""
    while True:
        chars = string.ascii_uppercase + string.digits
        part1 = ''.join(random.choices(chars, k=3))
        part2 = ''.join(random.choices(chars, k=2))
        code = f"{part1}-{part2}"
        if code not in lobbies:
            return code

def get_player_list(room_code):
    """Return a serializable list of players in a lobby."""
    lobby = lobbies.get(room_code)
    if not lobby:
        return []
    return [
        {
            "sid": sid,
            "name": p["name"],
            "avatar": p["avatar"],
            "health": p["health"],
            "xp": p["xp"],
            "is_alive": p["is_alive"],
            "is_host": sid == lobby["host_sid"]
        }
        for sid, p in lobby["players"].items()
    ]

def get_lobby_state(room_code):
    """Return full lobby state for broadcasting."""
    lobby = lobbies.get(room_code)
    if not lobby:
        return None
    return {
        "room_code": room_code,
        "phase": lobby["phase"],
        "work_duration": lobby["work_duration"],
        "break_duration": lobby["break_duration"],
        "timer_remaining": lobby["timer_remaining"],
        "players": get_player_list(room_code),
        "blocked_sites": lobby["blocked_sites"]
    }


# ─────────────────────────────────────────────
# DATABASE (existing — unchanged)
# ─────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect('instance/focus_fighter.db')
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────
# EXISTING ROUTES (unchanged)
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/arsenal')
def arsenal():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM player').fetchall()
    
    characters = []
    for p in players:
        items_db = conn.execute('SELECT * FROM inventory WHERE player_id = ?', (p['id'],)).fetchall()
        inventory = []
        for item in items_db:
            effects = json.loads(item['effects_json']) if item['effects_json'] else {}
            inventory.append(Item(
                name=item['name'],
                icon=item['icon'],
                rarity=item['rarity'],
                item_type=item['type'],
                stat=item['stat'],
                value=item['value'],
                effects=effects
            ))
            
        characters.append(Character(
            name=p['username'],
            level=p['level'],
            role="Sovereign" if p['level'] > 10 else "Acolyte",
            avatar_img=p['selected_char'] or 'char1.png',
            stats={
                "intellect": p['intellect'],
                "stamina": p['stamina'],
                "focus": p['focus'],
                "creativity": p['creativity']
            },
            inventory=inventory
        ))
    conn.close()
    
    html = render_arsenal(characters)
    return Response(html, mimetype='text/html')

@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    players_db = conn.execute('SELECT * FROM player ORDER BY xp DESC').fetchall()
    
    players_list = []
    for p in players_db:
        players_list.append({
            "id": p['id'],
            "username": p['username'],
            "avatar": p['selected_char'] or 'char1.png',
            "xp": p['xp'],
            "level": p['level'],
            "stats": {
                "intellect": p['intellect'],
                "stamina": p['stamina'],
                "focus": p['focus'],
                "creativity": p['creativity']
            }
        })
    conn.close()
    
    html = render_leaderboard(players_list)
    return Response(html, mimetype='text/html')


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: CREATE LOBBY
# ─────────────────────────────────────────────
@socketio.on('create_lobby')
def handle_create_lobby(data):
    """Host creates a new lobby. Returns the room code."""
    from flask import request
    sid = request.sid
    room_code = generate_room_code()

    lobbies[room_code] = {
        "host_sid": sid,
        "players": {
            sid: {
                "name": data.get("name", "Host"),
                "avatar": data.get("avatar", "char1.png"),
                "health": 100,
                "xp": 0,
                "is_alive": True
            }
        },
        "phase": "lobby",
        "work_duration": data.get("work_duration", 1500),   # default 25 min
        "break_duration": data.get("break_duration", 300),   # default 5 min
        "timer_remaining": data.get("work_duration", 1500),
        "blocked_sites": [],
        "focus_requests": {}
    }

    sid_to_room[sid] = room_code
    join_room(room_code)

    emit('lobby_created', {
        "room_code": room_code,
        "lobby": get_lobby_state(room_code)
    })
    print(f"[LOBBY] Created room {room_code} by {data.get('name', 'Host')}")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: JOIN LOBBY
# ─────────────────────────────────────────────
@socketio.on('join_lobby')
def handle_join_lobby(data):
    """Player joins an existing lobby by room code."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    name = data.get("name", "Player")
    avatar = data.get("avatar", "char1.png")

    # Validate room exists
    if room_code not in lobbies:
        emit('error', {"message": "Room not found. Check the code and try again."})
        return

    lobby = lobbies[room_code]

    # Max 4 players
    if len(lobby["players"]) >= 4:
        emit('error', {"message": "Lobby is full (4/4 players)."})
        return

    # Game already started
    if lobby["phase"] != "lobby":
        emit('error', {"message": "Game already in progress."})
        return

    # Add player
    lobby["players"][sid] = {
        "name": name,
        "avatar": avatar,
        "health": 100,
        "xp": 0,
        "is_alive": True
    }

    sid_to_room[sid] = room_code
    join_room(room_code)

    # Broadcast updated player list to everyone in the room
    emit('player_joined', {
        "player": {"sid": sid, "name": name, "avatar": avatar},
        "players": get_player_list(room_code),
        "player_count": len(lobby["players"])
    }, room=room_code)

    print(f"[LOBBY] {name} joined room {room_code} ({len(lobby['players'])}/4)")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: LOBBY SETTINGS (timer sync during setup)
# ─────────────────────────────────────────────
@socketio.on('lobby_settings')
def handle_lobby_settings(data):
    """Host broadcasts timer/break settings to all guests in the lobby."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]
    if sid != lobby["host_sid"]:
        return

    emit('lobby_settings_updated', {
        "settings": data.get("settings", {})
    }, room=room_code, include_self=False)


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: START GAME
# ─────────────────────────────────────────────
@socketio.on('start_game')
def handle_start_game(data):
    """Host starts the game. Requires all 4 players."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        emit('error', {"message": "Room not found."})
        return

    lobby = lobbies[room_code]

    # Only host can start
    if sid != lobby["host_sid"]:
        emit('error', {"message": "Only the host can start the game."})
        return

    # Need all 4 players
    if len(lobby["players"]) < 4:
        emit('error', {"message": f"Need 4 players to start. Currently {len(lobby['players'])}/4."})
        return

    # Update phase + apply custom durations from data if provided
    lobby["work_duration"] = data.get("work_duration", lobby["work_duration"])
    lobby["break_duration"] = data.get("break_duration", lobby["break_duration"])
    lobby["timer_remaining"] = lobby["work_duration"]
    lobby["phase"] = "work"

    # Reset all player health/alive status
    for p in lobby["players"].values():
        p["health"] = 100
        p["is_alive"] = True

    emit('game_started', {
        "lobby": get_lobby_state(room_code)
    }, room=room_code)

    print(f"[GAME] Room {room_code} started! Phase: WORK ({lobby['work_duration']}s)")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: BOSS ATTACK
# ─────────────────────────────────────────────
@socketio.on('boss_attack')
def handle_boss_attack(data):
    """
    Triggered when a player visits a blocked site during work phase.
    - All players lose 10 HP
    - Offender loses 20 XP per 5s tick (handled by repeated client emits)
    - If anyone dies → session fails
    """
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    # Only attack during work phase
    if lobby["phase"] != "work":
        return

    offender_name = lobby["players"].get(sid, {}).get("name", "Unknown")
    blocked_url = data.get("url", "unknown")
    is_sustained = data.get("sustained", False)  # True = 5s tick, False = initial hit

    dead_players = []

    if is_sustained:
        # Sustained penalty: offender loses 20 XP + heavy health damage
        if sid in lobby["players"]:
            lobby["players"][sid]["xp"] = max(0, lobby["players"][sid]["xp"] - 20)
            lobby["players"][sid]["health"] = max(0, lobby["players"][sid]["health"] - 15)
    else:
        # Initial hit: ALL players lose 10 HP
        for player_sid, player in lobby["players"].items():
            if player["is_alive"]:
                player["health"] = max(0, player["health"] - 10)

    # Check for deaths
    for player_sid, player in lobby["players"].items():
        if player["health"] <= 0 and player["is_alive"]:
            player["is_alive"] = False
            dead_players.append(player_sid)

    # If anyone died → session fails
    if dead_players:
        # All players lose 10 XP, offender loses 20 XP
        for player_sid, player in lobby["players"].items():
            player["xp"] = max(0, player["xp"] - 10)
        if sid in lobby["players"]:
            lobby["players"][sid]["xp"] = max(0, lobby["players"][sid]["xp"] - 20)

        lobby["phase"] = "failed"

        emit('game_over', {
            "result": "failed",
            "reason": f"{offender_name} was slain! The team falls.",
            "killed_by": blocked_url,
            "offender": offender_name,
            "players": get_player_list(room_code)
        }, room=room_code)

        print(f"[GAME] Room {room_code} FAILED — {offender_name} died on {blocked_url}")
        return

    # Broadcast the attack to all players
    emit('boss_attack_broadcast', {
        "offender_sid": sid,
        "offender_name": offender_name,
        "url": blocked_url,
        "sustained": is_sustained,
        "players": get_player_list(room_code)
    }, room=room_code)

    print(f"[BOSS] {offender_name} visited {blocked_url} in room {room_code} {'(sustained)' if is_sustained else '(initial)'}")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: XP UPDATE
# ─────────────────────────────────────────────
@socketio.on('xp_update')
def handle_xp_update(data):
    """
    Update and broadcast XP changes.
    Types: "win" (all +150), "death" (all -10, offender -20), "violation" (offender -20)
    """
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    update_type = data.get("type", "")

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    if update_type == "win":
        # Session win: all players get 150 XP
        for player in lobby["players"].values():
            player["xp"] += 150

    elif update_type == "death":
        # Death: all lose 10, offender loses additional 20
        offender_sid = data.get("offender_sid", sid)
        for player_sid, player in lobby["players"].items():
            player["xp"] = max(0, player["xp"] - 10)
        if offender_sid in lobby["players"]:
            lobby["players"][offender_sid]["xp"] = max(0, lobby["players"][offender_sid]["xp"] - 20)

    elif update_type == "violation":
        # Continuous violation: offender loses 20 XP
        if sid in lobby["players"]:
            lobby["players"][sid]["xp"] = max(0, lobby["players"][sid]["xp"] - 20)

    emit('xp_updated', {
        "type": update_type,
        "players": get_player_list(room_code)
    }, room=room_code)


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: PHASE CHANGE
# ─────────────────────────────────────────────
@socketio.on('phase_change')
def handle_phase_change(data):
    """
    Timer switches between work and break phases.
    Also handles the win condition: if all work phases are survived.
    """
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    new_phase = data.get("phase", "")

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    # Only host can trigger phase change
    if sid != lobby["host_sid"]:
        return

    if new_phase == "work":
        lobby["phase"] = "work"
        lobby["timer_remaining"] = lobby["work_duration"]
    elif new_phase == "break":
        lobby["phase"] = "break"
        lobby["timer_remaining"] = lobby["break_duration"]
    elif new_phase == "won":
        lobby["phase"] = "won"
        lobby["timer_remaining"] = 0
        # Award XP on win
        for player in lobby["players"].values():
            player["xp"] += 150

        emit('game_over', {
            "result": "won",
            "reason": "All work phases survived! The team is victorious!",
            "players": get_player_list(room_code)
        }, room=room_code)

        print(f"[GAME] Room {room_code} WON! All players earn 150 XP.")
        return

    emit('phase_changed', {
        "phase": lobby["phase"],
        "timer_remaining": lobby["timer_remaining"],
        "players": get_player_list(room_code)
    }, room=room_code)

    print(f"[PHASE] Room {room_code} → {lobby['phase'].upper()} ({lobby['timer_remaining']}s)")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: TIMER SYNC
# ─────────────────────────────────────────────
@socketio.on('timer_sync')
def handle_timer_sync(data):
    """Host broadcasts the current timer value to keep all clients in sync."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]
    if sid != lobby["host_sid"]:
        return

    lobby["timer_remaining"] = data.get("timer_remaining", lobby["timer_remaining"])

    emit('timer_synced', {
        "timer_remaining": lobby["timer_remaining"],
        "phase": lobby["phase"]
    }, room=room_code, include_self=False)


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: FOCUS REQUEST
# ─────────────────────────────────────────────
@socketio.on('focus_request')
def handle_focus_request(data):
    """Player requests focus mode for a set duration. Team must approve."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    duration = data.get("duration", 300)  # default 5 min

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]
    requester_name = lobby["players"].get(sid, {}).get("name", "Unknown")

    lobby["focus_requests"][sid] = {
        "duration": duration,
        "approved_by": [sid]  # requester auto-approves
    }

    emit('focus_requested', {
        "requester_sid": sid,
        "requester_name": requester_name,
        "duration": duration,
        "approvals": 1,
        "needed": len(lobby["players"])
    }, room=room_code)

    print(f"[FOCUS] {requester_name} requested focus mode for {duration}s in room {room_code}")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: FOCUS APPROVED
# ─────────────────────────────────────────────
@socketio.on('focus_approved')
def handle_focus_approved(data):
    """A player approves a focus mode request."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    requester_sid = data.get("requester_sid", "")

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    if requester_sid not in lobby["focus_requests"]:
        return

    focus_req = lobby["focus_requests"][requester_sid]

    # Don't double-count
    if sid not in focus_req["approved_by"]:
        focus_req["approved_by"].append(sid)

    approvals = len(focus_req["approved_by"])
    needed = len(lobby["players"])
    requester_name = lobby["players"].get(requester_sid, {}).get("name", "Unknown")

    if approvals >= needed:
        # All approved — activate focus mode
        emit('focus_activated', {
            "requester_sid": requester_sid,
            "requester_name": requester_name,
            "duration": focus_req["duration"]
        }, room=room_code)

        # Clean up the request
        del lobby["focus_requests"][requester_sid]
        print(f"[FOCUS] Approved! {requester_name} entering focus mode for {focus_req['duration']}s")
    else:
        emit('focus_vote_update', {
            "requester_sid": requester_sid,
            "requester_name": requester_name,
            "approvals": approvals,
            "needed": needed
        }, room=room_code)


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: BLOCKED SITE MANAGEMENT
# ─────────────────────────────────────────────
@socketio.on('propose_blocked_site')
def handle_propose_blocked_site(data):
    """A player proposes a website to block. Requires unanimous team approval."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    url = data.get("url", "").lower().strip()

    if room_code not in lobbies or not url:
        return

    lobby = lobbies[room_code]
    proposer_name = lobby["players"].get(sid, {}).get("name", "Unknown")

    # Check if already proposed
    for site in lobby["blocked_sites"]:
        if site["url"] == url:
            emit('error', {"message": f"{url} is already on the list."})
            return

    lobby["blocked_sites"].append({
        "url": url,
        "approved_by": [sid],  # proposer auto-approves
        "is_active": False
    })

    emit('blocked_site_proposed', {
        "url": url,
        "proposed_by": proposer_name,
        "approvals": 1,
        "needed": len(lobby["players"]),
        "blocked_sites": lobby["blocked_sites"]
    }, room=room_code)


@socketio.on('approve_blocked_site')
def handle_approve_blocked_site(data):
    """A player approves a proposed blocked site."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    url = data.get("url", "").lower().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    for site in lobby["blocked_sites"]:
        if site["url"] == url:
            if sid not in site["approved_by"]:
                site["approved_by"].append(sid)

            # Check if unanimously approved
            if len(site["approved_by"]) >= len(lobby["players"]):
                site["is_active"] = True

            emit('blocked_site_updated', {
                "url": url,
                "approvals": len(site["approved_by"]),
                "needed": len(lobby["players"]),
                "is_active": site["is_active"],
                "blocked_sites": lobby["blocked_sites"]
            }, room=room_code)
            return


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: GAME OVER
# ─────────────────────────────────────────────
@socketio.on('game_over')
def handle_game_over(data):
    """Host triggers game over (win or loss). Broadcasts to all players."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()
    result = data.get("result", "failed")  # "won" or "failed"

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]

    # Only host can trigger game over
    if sid != lobby["host_sid"]:
        return

    lobby["phase"] = result

    emit('game_over', {
        "result": result,
        "reason": data.get("reason", "Game ended."),
        "players": get_player_list(room_code)
    }, room=room_code)

    print(f"[GAME] Room {room_code} ended — result: {result}")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: HOST REDIRECT (Back to Home)
# ─────────────────────────────────────────────
@socketio.on('host_redirect')
def handle_host_redirect(data):
    """Host clicks Back to Home — all players are redirected."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]
    if sid != lobby["host_sid"]:
        return

    emit('redirect_home', {
        "message": "Host ended the session. Returning to home."
    }, room=room_code)

    # Cleanup: remove all players from tracking
    for player_sid in list(lobby["players"].keys()):
        if player_sid in sid_to_room:
            del sid_to_room[player_sid]

    del lobbies[room_code]
    print(f"[LOBBY] Room {room_code} dissolved by host.")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: PLAYER DISCONNECT
# ─────────────────────────────────────────────
@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection — notify remaining players."""
    from flask import request
    sid = request.sid

    room_code = sid_to_room.get(sid)
    if not room_code or room_code not in lobbies:
        if sid in sid_to_room:
            del sid_to_room[sid]
        return

    lobby = lobbies[room_code]
    player = lobby["players"].pop(sid, None)
    player_name = player["name"] if player else "Unknown"

    if sid in sid_to_room:
        del sid_to_room[sid]

    # If host left, dissolve the lobby
    if sid == lobby["host_sid"]:
        emit('lobby_dissolved', {
            "message": f"Host ({player_name}) disconnected. Lobby closed."
        }, room=room_code)

        # Cleanup all remaining players
        for remaining_sid in list(lobby["players"].keys()):
            if remaining_sid in sid_to_room:
                del sid_to_room[remaining_sid]

        del lobbies[room_code]
        print(f"[LOBBY] Room {room_code} dissolved — host {player_name} disconnected.")
        return

    # Non-host left — notify remaining players
    emit('player_left', {
        "player_name": player_name,
        "player_sid": sid,
        "players": get_player_list(room_code),
        "player_count": len(lobby["players"])
    }, room=room_code)

    print(f"[LOBBY] {player_name} left room {room_code} ({len(lobby['players'])}/4)")


# ─────────────────────────────────────────────
# SOCKET.IO EVENT: REPLAY (host restarts session)
# ─────────────────────────────────────────────
@socketio.on('replay')
def handle_replay(data):
    """Host clicks Replay — reset health/phase, keep players."""
    from flask import request
    sid = request.sid
    room_code = data.get("room_code", "").upper().strip()

    if room_code not in lobbies:
        return

    lobby = lobbies[room_code]
    if sid != lobby["host_sid"]:
        return

    # Reset state
    lobby["phase"] = "lobby"
    lobby["timer_remaining"] = lobby["work_duration"]
    lobby["focus_requests"] = {}

    for player in lobby["players"].values():
        player["health"] = 100
        player["is_alive"] = True

    emit('game_restarted', {
        "lobby": get_lobby_state(room_code)
    }, room=room_code)

    print(f"[GAME] Room {room_code} restarted by host.")


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
if __name__ == '__main__':
    # Ensure instance directory exists
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
        
    # Auto-move bg_gif.gif to static folder if it's currently in the root
    if os.path.exists('bg_gif.gif') and not os.path.exists(os.path.join('static', 'bg_gif.gif')):
        try:
            shutil.move('bg_gif.gif', os.path.join('static', 'bg_gif.gif'))
            print("Successfully moved 'bg_gif.gif' to the 'static' folder.")
        except Exception as e:
            print(f"Failed to move 'bg_gif.gif': {e}")
            
    # Find local IP to display
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    print("="*50)
    print("Starting The Last Braincell...")
    print(f"Open this link in your browser: http://127.0.0.1:5000")
    print(f"Or on your local network: http://{local_ip}:5000")
    print(f"WebSocket real-time multiplayer: ENABLED")
    print("="*50)
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
