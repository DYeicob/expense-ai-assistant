#!/usr/bin/env python3
"""
Script to create the SQLite database file (expenses.db)
This creates an empty database with all tables defined in the models
"""
import sys
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from backend.models.database import Base, engine, init_db
from backend.models import tables
from backend.config.constants import EXPENSE_CATEGORIES

def create_database():
    """Create empty database with all tables"""
    print("🗄️  Creating database...")
    
    # Create database directory if it doesn't exist
    db_dir = Path("data/database")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print(f"✅ Database created at: {db_dir}/expenses.db")
    print("\n📊 Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
    
    # Optionally populate with categories
    from backend.models.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Check if categories exist
        existing = db.query(tables.Category).count()
        
        if existing == 0:
            print("\n📝 Populating categories...")
            for slug, info in EXPENSE_CATEGORIES.items():
                category = tables.Category(
                    name=info["name"],
                    slug=slug,
                    color=info["color"],
                    icon=info["icon"],
                    keywords=info["keywords"]
                )
                db.add(category)
            
            db.commit()
            print(f"✅ Added {len(EXPENSE_CATEGORIES)} categories")
        else:
            print(f"\n✅ Database already has {existing} categories")
    
    except Exception as e:
        print(f"⚠️  Error populating categories: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n✅ Database ready to use!")
    print("\n📌 Next steps:")
    print("  1. Run: python scripts/init_db.py (to add sample data)")
    print("  2. Or start using the app: ./start.sh")

if __name__ == "__main__":
    create_database()