#!/usr/bin/env python3
"""
Database setup script for SmartBiz360 Backend
This script helps set up the PostgreSQL database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

def setup_database():
    """Set up the PostgreSQL database and user"""
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration from environment or use defaults
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_name = os.getenv('DB_NAME', 'smartbiz360')
    
    print("Setting up SmartBiz360 database...")
    print(f"Host: {db_host}")
    print(f"Port: {db_port}")
    print(f"Database: {db_name}")
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        # Close connection to server
        cursor.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('products', 'customers', 'orders', 'order_items')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if not existing_tables:
            print("No existing tables found. Run 'python init_db.py' to create tables and sample data.")
        else:
            print(f"Found existing tables: {', '.join(existing_tables)}")
            print("Database is ready to use!")
        
        cursor.close()
        conn.close()
        
        # Update .env file with database URL
        env_file = '.env'
        if not os.path.exists(env_file):
            print("\nCreating .env file...")
            with open(env_file, 'w') as f:
                f.write(f"""# Database Configuration
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
""")
            print(".env file created successfully!")
        else:
            print("\n.env file already exists.")
        
        print("\nDatabase setup completed!")
        print("Next steps:")
        print("1. Run 'python init_db.py' to create tables and sample data")
        print("2. Run 'python start.py' to start the API server")
        
    except psycopg2.Error as e:
        print(f"Database setup failed: {e}")
        print("\nMake sure PostgreSQL is running and accessible.")
        print("You may need to:")
        print("1. Install PostgreSQL")
        print("2. Start PostgreSQL service")
        print("3. Check your connection credentials")
        return False
    
    return True

if __name__ == '__main__':
    setup_database()
