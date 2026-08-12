import sqlite3

def fix_database():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    # Missing columns aur tables ki list
    queries = [
        "ALTER TABLE store_storesetting ADD COLUMN festival_music_url VARCHAR(500);",
        "ALTER TABLE store_storesetting ADD COLUMN bg_music_link VARCHAR(500);",
        "ALTER TABLE store_product ADD COLUMN display_section VARCHAR(20) DEFAULT 'trending';",
        "ALTER TABLE store_product ADD COLUMN section VARCHAR(20) DEFAULT 'trending';",
        "CREATE TABLE IF NOT EXISTS store_videoreview (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), thumbnail_url VARCHAR(200), video_url VARCHAR(200), is_active bool);",
        "CREATE TABLE IF NOT EXISTS store_storevideoreview (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), thumbnail_url VARCHAR(200), video_url VARCHAR(200), is_active bool);"
    ]
    
    for q in queries:
        try:
            c.execute(q)
            print(f"Success: {q}")
        except Exception as e:
            # Agar column pehle se hoga toh error ko ignore kar dega
            pass
            
    conn.commit()
    conn.close()
    print("Database Fix Completed!")

if __name__ == "__main__":
    fix_database()