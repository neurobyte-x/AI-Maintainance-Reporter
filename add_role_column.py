import sqlite3

def migrate_db():
    """Add role column to users table if it doesn't exist"""
    conn = sqlite3.connect("maintenance_tickets.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role' not in columns:
            print("Adding 'role' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ 'role' column already exists. No migration needed.")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
