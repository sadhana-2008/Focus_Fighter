from flask import Flask, render_template, send_from_directory, Response
import os
import sqlite3
import json
import socket
import shutil
from Leader_board.arsenal import Character, Item, render_arsenal
from Leader_board.leaderboard import render_leaderboard

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('instance/focus_fighter.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        # Fetch inventory for this player
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
    # Order by XP descending
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
    print("Starting Focus Fighter Web App...")
    print(f"Open this link in your browser: http://127.0.0.1:5000")
    print(f"Or on your local network: http://{local_ip}:5000")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
