from flask import Flask, render_template, send_from_directory, jsonify, request
import os
import socket
import shutil
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///focus_fighter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    selected_char = db.Column(db.String(120), default='char1.png')
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    health = db.Column(db.Integer, default=100)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=10)
    speed = db.Column(db.Integer, default=10)

    def to_dict(self):
        return {
            "username": self.username,
            "selected_char": self.selected_char,
            "xp": self.xp,
            "level": self.level,
            "stats": {
                "health": self.health,
                "attack": self.attack,
                "defense": self.defense,
                "speed": self.speed
            }
        }

# ─────────────────────────────────────────────
# IN-MEMORY TEAM DATABASE (Group Points System)
# ─────────────────────────────────────────────
teams_db = {
    "team_alpha": {"id": "team_alpha", "name": "Team Alpha", "points": 1500, "emblem": "🦅"},
    "team_titan": {"id": "team_titan", "name": "Team Titan", "points": 1250, "emblem": "⚔️"},
    "team_omega": {"id": "team_omega", "name": "Team Omega", "points": 800,  "emblem": "🐺"},
    "team_nova":  {"id": "team_nova",  "name": "Team Nova",  "points": 500,  "emblem": "🌟"},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/arsenal')
def arsenal():
    return render_template('arsenal.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

# GET all teams sorted by points
@app.route('/api/teams', methods=['GET'])
def get_teams():
    sorted_teams = sorted(teams_db.values(), key=lambda t: int(t['points']), reverse=True)
    return jsonify(sorted_teams)

# Transfer points from defeated team to victor
@app.route('/api/transfer_points', methods=['POST'])
def transfer_points():
    data = request.json
    victor_id = data.get('victor_id')
    defeated_id = data.get('defeated_id')
    if victor_id in teams_db and defeated_id in teams_db:
        stolen = int(teams_db[defeated_id]['points'])
        teams_db[victor_id]['points'] = int(teams_db[victor_id]['points']) + stolen
        teams_db[defeated_id]['points'] = 0
        return jsonify({"success": True, "transferred": stolen})
    return jsonify({"success": False, "message": "Invalid team IDs"}), 400

# Spend points on a quest or relic
@app.route('/api/spend_points', methods=['POST'])
def spend_points():
    data = request.json
    team_id = data.get('team_id')
    cost = int(data.get('cost', 0))
    if team_id in teams_db:
        current = int(teams_db[team_id]['points'])
        if current >= cost:
            teams_db[team_id]['points'] = current - cost
            return jsonify({"success": True, "remaining": teams_db[team_id]['points']})
        return jsonify({"success": False, "message": "Not enough points"}), 400
    return jsonify({"success": False, "message": "Invalid team ID"}), 400

# Penalise team for distraction
@app.route('/api/distraction_penalty', methods=['POST'])
def distraction_penalty():
    data = request.json
    team_id = data.get('team_id')
    penalty = int(data.get('penalty', 50))
    if team_id in teams_db:
        current = int(teams_db[team_id]['points'])
        teams_db[team_id]['points'] = max(0, current - penalty)
        return jsonify({"success": True, "lost": penalty, "remaining": teams_db[team_id]['points']})
    return jsonify({"success": False, "message": "Invalid team ID"}), 400

@app.route('/api/player', methods=['POST'])
def update_player():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    player = Player.query.filter_by(username=username).first()
    if not player:
        player = Player(username=username)
        db.session.add(player)
    
    player.selected_char = data.get('selected_char', player.selected_char)
    player.xp = data.get('xp', player.xp)
    player.level = data.get('level', player.level)
    
    stats = data.get('stats', {})
    player.health = stats.get('health', player.health)
    player.attack = stats.get('attack', player.attack)
    player.defense = stats.get('defense', player.defense)
    player.speed = stats.get('speed', player.speed)
    
    db.session.commit()
    return jsonify(player.to_dict())

@app.route('/api/player/<username>', methods=['GET'])
def get_player(username):
    player = Player.query.filter_by(username=username).first()
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player.to_dict())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
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
    local_ip = socket.gethostbyname(hostname)
    
    print("="*50)
    print("Starting Focus Fighter Web App with Database...")
    print(f"Open this link in your browser: http://127.0.0.1:5000")
    print(f"Or on your local network: http://{local_ip}:5000")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
