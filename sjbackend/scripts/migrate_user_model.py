# scripts/migrate_user_model.py
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent  # Go up one level from scripts to project root
sys.path.insert(0, str(project_root))

import mysql.connector
from app.core.config import settings

def run_migration():
    """Add new columns to users table"""
    print("🔄 Starting migration...")
    
    # Parse database URL
    db_url = settings.DATABASE_URL
    print(f"📊 Database URL: {db_url}")
    
    # Format: mysql+mysqlconnector://user:password@host:port/database
    try:
        # Remove protocol prefix
        clean_url = db_url.replace('mysql+mysqlconnector://', '')
        
        # Split into auth/host and database
        parts = clean_url.split('/')
        database = parts[1] if len(parts) > 1 else 'siriusjobs_v2'
        
        # Split auth and host
        auth_host = parts[0].split('@')
        user_pass = auth_host[0].split(':')
        host_port = auth_host[1].split(':')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '3306'
        
        print(f"🔌 Connecting to MySQL at {host}:{port} as {user}")
        
        # Connect to database
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port)
        )
        
        cursor = conn.cursor()
        print("✅ Connected to database")
        
        # Check existing columns
        cursor.execute("SHOW COLUMNS FROM users")
        existing_columns = [column[0] for column in cursor.fetchall()]
        print(f"📋 Existing columns: {len(existing_columns)}")
        
        # Columns to add
        migrations = [
            ("govt_id_url", "ALTER TABLE users ADD COLUMN govt_id_url VARCHAR(500) NULL"),
            ("govt_id_type", "ALTER TABLE users ADD COLUMN govt_id_type VARCHAR(50) NULL"),
            ("id_verified_at", "ALTER TABLE users ADD COLUMN id_verified_at TIMESTAMP NULL"),
            ("guarantor_name", "ALTER TABLE users ADD COLUMN guarantor_name VARCHAR(255) NULL"),
            ("guarantor_phone", "ALTER TABLE users ADD COLUMN guarantor_phone VARCHAR(50) NULL"),
            ("guarantor_email", "ALTER TABLE users ADD COLUMN guarantor_email VARCHAR(255) NULL"),
            ("profile_views", "ALTER TABLE users ADD COLUMN profile_views INT DEFAULT 0"),
            ("subscription_status", "ALTER TABLE users ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'inactive'"),
            ("subscription_end_date", "ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP NULL")
        ]
        
        added_count = 0
        skipped_count = 0
        
        for column_name, migration_sql in migrations:
            if column_name not in existing_columns:
                try:
                    cursor.execute(migration_sql)
                    print(f"  ✅ Added: {column_name}")
                    added_count += 1
                except Exception as e:
                    print(f"  ❌ Error adding {column_name}: {e}")
            else:
                print(f"  ⏭️ Skipped: {column_name} (already exists)")
                skipped_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Migration completed!")
        print(f"   Added: {added_count} columns")
        print(f"   Skipped: {skipped_count} columns")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()