import sqlite3
import os

db_path = 'instance/focus_fighter.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    for table in tables:
        table_name = table[0]
        print(f"\nSchema for {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        info = cursor.fetchall()
        for col in info:
            print(col)
            
        print(f"\nData sample for {table_name}:")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        data = cursor.fetchall()
        for row in data:
            print(row)
            
    conn.close()
