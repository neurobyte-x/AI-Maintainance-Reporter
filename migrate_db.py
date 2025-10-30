import sqlite3
import os

def migrate_database():
    """Migrate the database to add user_id column to tickets table"""
    
    db_path = "maintenance_tickets.db"
    
    if not os.path.exists(db_path):
        print("✅ No existing database found. New database will be created with correct schema.")
        return
    
    print("🔄 Migrating database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "user_id" in columns:
            print("✅ Database already migrated. user_id column exists.")
            conn.close()
            return
        
        print("📋 Creating users table if not exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("📋 Adding user_id column to tickets table...")
        
        # Create a default user for existing tickets
        cursor.execute("""
            INSERT OR IGNORE INTO users (email, password_hash, full_name)
            VALUES ('admin@reva.edu.in', 'default_hash', 'System Admin')
        """)
        
        cursor.execute("SELECT id FROM users WHERE email = 'admin@reva.edu.in'")
        default_user_id = cursor.fetchone()[0]
        
        # Add user_id column with default value
        cursor.execute(f"ALTER TABLE tickets ADD COLUMN user_id INTEGER DEFAULT {default_user_id}")
        
        # Update all existing tickets to have the default user_id
        cursor.execute(f"UPDATE tickets SET user_id = {default_user_id} WHERE user_id IS NULL")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        print(f"   - Added user_id column to tickets table")
        print(f"   - Created default user (admin@reva.edu.in)")
        print(f"   - Assigned existing tickets to default user")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
    print("\n✅ Migration complete! You can now restart your application.")
