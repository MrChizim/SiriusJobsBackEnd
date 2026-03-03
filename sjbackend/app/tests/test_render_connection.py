# test_render_connection.py
import psycopg2
from urllib.parse import urlparse

# Your Render database details
DATABASE_URL = "postgresql://sirius_user:ZALHW4W9gK3L6dSHZTSI0FVGjIcW7AFr@dpg-d6ionhogjchc73dgbt5g-a.frankfurt-postgres.render.com/siriusjobs_v2"

print("🔌 Testing connection to Render PostgreSQL...")
print("-" * 50)

try:
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connected successfully!")
    print(f"📊 PostgreSQL version: {version[0][:50]}...")
    
    # Check if any tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n📋 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("\n📋 No tables found. Ready to create schema.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Make sure your IP is allowed in Render")
    print("2. Check if database is active in Render dashboard")
    print("3. Verify the password is correct")