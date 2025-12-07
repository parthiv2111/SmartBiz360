#!/usr/bin/env python3
"""
Fix database by creating all missing tables using db.create_all()
Then stamp migrations as current
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask app before importing models
os.environ['FLASK_APP'] = 'app.py'

from app import app, db
# Import all models to ensure they're registered
from models import (
    User, UserSettings, Product, Customer, Order, OrderItem,
    Attendance, Project, Task, Lead, Deal, Expense, Supplier,
    PurchaseOrder, PasswordResetOTP
)

def fix_database():
    """Create all tables and stamp migrations"""
    
    print("🔧 Fixing database...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Create all tables using SQLAlchemy
            print("\n📦 Creating all database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Check what tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Found {len(tables)} tables in database:")
            for table in sorted(tables):
                print(f"   - {table}")
            
            # Stamp migrations as current (mark all migrations as applied)
            print("\n🏷️  Stamping migrations as current...")
            from flask_migrate import stamp
            try:
                # Get the latest migration revision
                from alembic.config import Config
                from alembic.script import ScriptDirectory
                
                alembic_cfg = Config('migrations/alembic.ini')
                script = ScriptDirectory.from_config(alembic_cfg)
                head = script.get_current_head()
                
                if head:
                    stamp(revision=head)
                    print(f"✅ Migrations stamped to: {head}")
                else:
                    # If no head, find the latest merge revision
                    latest = '4f05409788e5'  # merge_all_heads
                    stamp(revision=latest)
                    print(f"✅ Migrations stamped to: {latest}")
            except Exception as e:
                print(f"⚠️  Could not stamp migrations: {e}")
                print("   You may need to run: flask db stamp head")
            
            print("\n🎉 Database fix completed!")
            print("\nYou can now:")
            print("1. Start the API server: python app.py")
            print("2. Create users through the registration endpoint")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error fixing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_database()
    sys.exit(0 if success else 1)

