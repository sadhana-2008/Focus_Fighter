import sqlite3
import os

db_path = 'instance/focus_fighter.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add new columns if they don't exist
    columns = [
        ('intellect', 'INTEGER DEFAULT 0'),
        ('stamina', 'INTEGER DEFAULT 0'),
        ('focus', 'INTEGER DEFAULT 0'),
        ('creativity', 'INTEGER DEFAULT 0')
    ]
    
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE player ADD COLUMN {col_name} {col_type};")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists")
            
    # Add sample data for WikiKnight and CodeWitch if not present
    players = [
        ('WikiKnight', 'char1.png', 1000, 14, 88, 72, 94, 45),
        ('CodeWitch', 'char2.png', 850, 12, 95, 40, 82, 98),
        ('ShadowNinja', 'char3.png', 1200, 15, 70, 85, 90, 60),
        ('PlasmaMage', 'char5.png', 950, 13, 92, 55, 88, 75)
    ]
    
    for username, avatar, xp, level, intellect, stamina, focus, creativity in players:
        cursor.execute("SELECT id FROM player WHERE username=?", (username,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO player (username, selected_char, xp, level, intellect, stamina, focus, creativity, health, attack, defense, speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 100, 50, 50, 50)
            """, (username, avatar, xp, level, intellect, stamina, focus, creativity))
            print(f"Added sample player: {username}")
            
    conn.commit()
    conn.close()
    print("Database update complete.")
