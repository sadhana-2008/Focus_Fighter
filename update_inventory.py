import sqlite3
import os
import json

db_path = 'instance/focus_fighter.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop and re-create inventory table to ensure new schema
    cursor.execute("DROP TABLE IF EXISTS inventory")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
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
    """)
    print("Created inventory table if it didn't exist.")
    
    # Add sample items for all players
    cursor.execute("DELETE FROM inventory")
    items = [
        # WikiKnight (id=1)
        (1, "Excalibur of Truth", "ph-sword", "weapon", "dmg", 50, "legendary", json.dumps({"foc": 10})),
        (1, "Shield of Focus", "ph-shield", "armor", "stm", 5, "epic", json.dumps({"def": 30})),
        (1, "Tome of Wisdom", "ph-book", "skill", "int", 20, "rare", json.dumps({})),
        (1, "Focus Elixir", "ph-flask", "consumable", "foc", 15, "common", json.dumps({})),
        # CodeWitch (id=2)
        (2, "Staff of the Void", "ph-magic-wand", "weapon", "dmg", 45, "epic", json.dumps({"int": 15})),
        (2, "Scroll of Recursion", "ph-scroll", "skill", "int", 25, "rare", json.dumps({"foc": 5})),
        (2, "Crystal of Clarity", "ph-crystal", "stat", "foc", 10, "common", json.dumps({})),
        # ShadowNinja (id=3)
        (3, "Kunai of Silence", "ph-knife", "weapon", "spd", 40, "epic", json.dumps({"dmg": 20})),
        (3, "Cloak of Mists", "ph-detective", "armor", "spd", 10, "rare", json.dumps({"def": 15})),
        (3, "Ninja XP Scroll", "ph-lightning", "consumable", "xp", 100, "rare", json.dumps({})),
        # PlasmaMage (id=4)
        (4, "Orb of Singularity", "ph-planet", "weapon", "dmg", 60, "legendary", json.dumps({"int": 20})),
        (4, "Ring of Nova", "ph-fingerprint", "stat", "int", 10, "rare", json.dumps({"stm": 5})),
    ]
    
    cursor.executemany("""
        INSERT INTO inventory (player_id, name, icon, type, stat, value, rarity, effects_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, items)
    print("Added detailed sample inventory items.")
            
    conn.commit()
    conn.close()
    print("Database update complete.")
