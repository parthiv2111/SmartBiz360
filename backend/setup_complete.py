#!/usr/bin/env python3
"""
Complete setup script for SmartBiz360 Backend
This script handles database setup, migrations, and initialization
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def setup_database():
    """Complete database setup"""
    
    print("🚀 Setting up SmartBiz360 Backend Database...")
    print("=" * 50)
    
    # Step 1: Create database
    if not run_command("python setup_db.py", "Database creation"):
        return False
    
    # Step 2: Set Flask app environment
    os.environ['FLASK_APP'] = 'app.py'
    print("✅ Flask app environment set")
    
    # Step 3: Initialize Flask-Migrate (if not already done)
    print("\n🔄 Initializing Flask-Migrate...")
    if not os.path.exists('migrations'):
        if not run_command("flask db init", "Flask-Migrate initialization"):
            print("⚠️  Flask-Migrate may already be initialized")
    
    # Step 4: Create migration for OTP table
    print("\n🔄 Creating migration for OTP table...")
    if not run_command("flask db migrate -m 'Add password reset OTP table'", "Migration creation"):
        print("⚠️  Migration may already exist")
    
    # Step 5: Run migration
    if not run_command("flask db upgrade", "Database migration"):
        return False
    
    # Step 6: Initialize database with sample data
    if not run_command("python init_db.py", "Database initialization"):
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure email settings in .env file (see EMAIL_SETUP.md)")
    print("2. Start the API server: python app.py")
    print("3. Start the frontend: cd ../new-frontend/smartbussiness360-47 && npm run dev")
    
    return True

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import flask
        import flask_sqlalchemy
        import flask_migrate
        import flask_cors
        import flask_jwt_extended
        import psycopg2
        import bcrypt
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    print("SmartBiz360 Backend Setup")
    print("=" * 30)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed!")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("Your SmartBiz360 backend is ready to use!")
