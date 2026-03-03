# create_tables.py
import psycopg2
from urllib.parse import urlparse

# Your Render database URL
DATABASE_URL = "postgresql://sirius_user:ZALHW4W9gK3L6dSHZTSI0FVGjIcW7AFr@dpg-d6ionhogjchc73dgbt5g-a.frankfurt-postgres.render.com/siriusjobs_v2"

print("🚀 Creating database tables on Render...")
print("=" * 60)

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✅ Connected to Render PostgreSQL")
    
    # =============================================
    # CREATE ENUM TYPES
    # =============================================
    print("\n📝 Creating enum types...")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE account_type AS ENUM ('worker', 'employer', 'professional', 'merchant', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("  ✅ account_type enum created")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE job_type_enum AS ENUM ('full_time', 'part_time', 'contract', 'project_based', 'temporary');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("  ✅ job_type_enum created")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE experience_level_enum AS ENUM ('entry_level', '1_3_years', '3_5_years', '5_plus_years');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("  ✅ experience_level_enum created")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE application_status AS ENUM ('pending', 'reviewed', 'shortlisted', 'rejected', 'hired', 'withdrawn');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("  ✅ application_status enum created")
    
    # =============================================
    # CREATE TABLES
    # =============================================
    print("\n📝 Creating tables...")
    
    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            account_type account_type NOT NULL,
            is_verified BOOLEAN DEFAULT FALSE,
            is_superuser BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            profile_image_url VARCHAR(500),
            location VARCHAR(255),
            bio TEXT,
            skills TEXT,
            govt_id_url VARCHAR(500),
            govt_id_type VARCHAR(50),
            id_verified_at TIMESTAMP,
            guarantor_name VARCHAR(255),
            guarantor_phone VARCHAR(50),
            guarantor_email VARCHAR(255),
            profile_views INTEGER DEFAULT 0,
            subscription_status VARCHAR(50) DEFAULT 'inactive',
            subscription_end_date TIMESTAMP,
            email_verified_at TIMESTAMP,
            phone_verified_at TIMESTAMP,
            identity_verified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ users table created")
    
    # EMPLOYER PROFILES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employer_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            company_name VARCHAR(255),
            company_website VARCHAR(255),
            company_size VARCHAR(50),
            industry VARCHAR(100),
            verified BOOLEAN DEFAULT FALSE,
            verification_doc_url VARCHAR(500),
            company_description TEXT,
            logo_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ employer_profiles table created")
    
    # JOBS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            employer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(100) NOT NULL,
            job_type job_type_enum NOT NULL DEFAULT 'full_time',
            experience_level experience_level_enum NOT NULL DEFAULT 'entry_level',
            location VARCHAR(255) NOT NULL,
            specific_address VARCHAR(500),
            is_remote BOOLEAN DEFAULT FALSE,
            budget_min FLOAT,
            budget_max FLOAT,
            budget_type VARCHAR(50) DEFAULT 'fixed',
            salary_currency VARCHAR(10) DEFAULT 'NGN',
            salary_period VARCHAR(20) DEFAULT 'monthly',
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            contact_phone VARCHAR(50) NOT NULL,
            show_contact BOOLEAN DEFAULT TRUE,
            skills_required JSONB,
            responsibilities TEXT,
            benefits TEXT,
            duration VARCHAR(100),
            status VARCHAR(50) DEFAULT 'open',
            expires_at TIMESTAMP,
            applications_count INTEGER DEFAULT 0,
            views_count INTEGER DEFAULT 0,
            save_count INTEGER DEFAULT 0,
            featured BOOLEAN DEFAULT FALSE,
            average_rating FLOAT DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("  ✅ jobs table created")
    
    # APPLICATIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            worker_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            cover_letter TEXT,
            expected_pay FLOAT,
            proposed_timeline VARCHAR(100),
            status application_status DEFAULT 'pending',
            employer_notes TEXT,
            rejection_reason TEXT,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            CONSTRAINT unique_application UNIQUE (job_id, worker_id)
        )
    """)
    print("  ✅ applications table created")
    
    # MERCHANT PROFILES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchant_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            business_name VARCHAR(255) NOT NULL,
            business_category VARCHAR(100) NOT NULL,
            business_description TEXT,
            business_address VARCHAR(500),
            business_phone VARCHAR(50),
            business_email VARCHAR(255),
            business_website VARCHAR(255),
            logo_url VARCHAR(500),
            banner_url VARCHAR(500),
            instagram VARCHAR(255),
            facebook VARCHAR(255),
            twitter VARCHAR(255),
            whatsapp VARCHAR(50),
            verified BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            featured BOOLEAN DEFAULT FALSE,
            total_products INTEGER DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            average_rating FLOAT DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            subscription_plan VARCHAR(50) DEFAULT 'free',
            subscription_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ merchant_profiles table created")
    
    # PRODUCTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL REFERENCES merchant_profiles(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            price FLOAT NOT NULL,
            compare_at_price FLOAT,
            cost_per_item FLOAT,
            profit_margin FLOAT,
            stock_quantity INTEGER DEFAULT 0,
            sku VARCHAR(100) UNIQUE,
            barcode VARCHAR(100),
            track_inventory BOOLEAN DEFAULT TRUE,
            allow_backorders BOOLEAN DEFAULT FALSE,
            images JSONB,
            videos JSONB,
            thumbnail VARCHAR(500),
            weight FLOAT,
            dimensions JSONB,
            materials JSONB,
            tags JSONB,
            variants JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            featured BOOLEAN DEFAULT FALSE,
            views_count INTEGER DEFAULT 0,
            sold_count INTEGER DEFAULT 0,
            average_rating FLOAT DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("  ✅ products table created")
    
    # ORDERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            merchant_id INTEGER NOT NULL REFERENCES merchant_profiles(id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'pending',
            payment_status VARCHAR(50) DEFAULT 'pending',
            payment_method VARCHAR(50),
            payment_reference VARCHAR(255),
            subtotal FLOAT DEFAULT 0,
            shipping_cost FLOAT DEFAULT 0,
            tax FLOAT DEFAULT 0,
            discount FLOAT DEFAULT 0,
            total FLOAT DEFAULT 0,
            shipping_address JSONB,
            shipping_method VARCHAR(100),
            tracking_number VARCHAR(255),
            customer_notes TEXT,
            merchant_notes TEXT,
            paid_at TIMESTAMP,
            shipped_at TIMESTAMP,
            delivered_at TIMESTAMP,
            cancelled_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("  ✅ orders table created")
    
    # ORDER ITEMS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1,
            price FLOAT NOT NULL,
            total FLOAT NOT NULL,
            product_name VARCHAR(255) NOT NULL,
            product_sku VARCHAR(100),
            product_image VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ order_items table created")
    
    # PRODUCT REVIEWS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_reviews (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            title VARCHAR(255),
            review TEXT,
            images JSONB,
            videos JSONB,
            verified_purchase BOOLEAN DEFAULT FALSE,
            helpful_count INTEGER DEFAULT 0,
            not_helpful_count INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ product_reviews table created")
    
    # RATINGS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id SERIAL PRIMARY KEY,
            rater_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            rated_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            job_id INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
            rating FLOAT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("  ✅ ratings table created")
    
    # PLATFORM STATS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_stats (
            id INTEGER PRIMARY KEY DEFAULT 1,
            total_users INTEGER DEFAULT 0,
            active_workers INTEGER DEFAULT 0,
            jobs_completed INTEGER DEFAULT 0,
            open_jobs INTEGER DEFAULT 0,
            satisfaction_rate FLOAT DEFAULT 0.0,
            total_reviews INTEGER DEFAULT 0,
            last_updated TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT platform_stats_single_row CHECK (id = 1)
        )
    """)
    print("  ✅ platform_stats table created")
    
    # Insert initial platform stats
    cursor.execute("""
        INSERT INTO platform_stats (id) VALUES (1) 
        ON CONFLICT (id) DO NOTHING
    """)
    print("  ✅ initial platform stats inserted")
    
    # =============================================
    # CREATE INDEXES
    # =============================================
    print("\n📝 Creating indexes for performance...")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_account_type ON users(account_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_employer ON jobs(employer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_merchant ON products(merchant_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_merchant ON orders(merchant_id)")
    
    print("  ✅ indexes created")
    
    # =============================================
    # VERIFICATION
    # =============================================
    print("\n📊 Verifying tables...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    print(f"\n✅ All tables created successfully! ({len(tables)} tables)")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update your .env file with:")
    print(f"   DATABASE_URL={DATABASE_URL}")
    print("2. Deploy your FastAPI app to Render")
    print("3. Test the connection with your app")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()