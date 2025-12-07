#!/usr/bin/env python3
"""
Run database migration for SmartBiz360 Backend
This script runs the Flask-Migrate upgrade command
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run database migration"""
    
    print("Running database migration...")
    
    try:
        # Set Flask app
        os.environ['FLASK_APP'] = 'app.py'
        
        # Run flask db upgrade
        result = subprocess.run(
            ['flask', 'db', 'upgrade'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print("✅ Database migration completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Database migration failed!")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("\n✅ Database is up to date!")
        print("You can now start the API server with: python app.py")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
