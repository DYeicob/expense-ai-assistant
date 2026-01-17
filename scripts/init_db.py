"""
Script to initialize the database with sample data
"""
import sys
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.models.database import init_db, SessionLocal
from backend.models import tables
from backend.config.constants import EXPENSE_CATEGORIES
from datetime import datetime, timedelta
import random

def create_sample_user(db):
    """Creates a sample demo user"""
    user = tables.User(
        email="demo@example.com",
        name="Demo User",
        hashed_password="hashed_password_here",  # Use real hash in production
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ User created: {user.email}")
    return user


def create_categories(db):
    """Creates the initial expense categories"""
    categories = []
    
    for slug, info in EXPENSE_CATEGORIES.items():
        existing = db.query(tables.Category).filter(
            tables.Category.slug == slug
        ).first()
        
        if not existing:
            category = tables.Category(
                name=info["name"],
                slug=slug,
                color=info["color"],
                icon=info["icon"],
                keywords=info["keywords"]
            )
            db.add(category)
            categories.append(category)
    
    db.commit()
    print(f"✅ {len(categories)} categories created")
    
    # Return all categories in DB
    return db.query(tables.Category).all()


def create_sample_expenses(db, user, categories):
    """Generates random sample expenses"""
    
    # Sample merchants by category
    merchants = {
        "food": ["Walmart", "Whole Foods", "Trader Joe's", "The Local Bistro"],
        "transportation": ["Shell", "Uber", "Public Transit", "Delta Airlines"],
        "housing": ["Electric Co", "Verizon", "Home Depot", "Rent Payment"],
        "health": ["CVS Pharmacy", "Planet Fitness", "Dental Clinic"],
        "leisure": ["Netflix", "Spotify", "AMC Theatres", "Steam"],
        "shopping": ["Zara", "Amazon", "Best Buy", "IKEA"],
        "education": ["Barnes & Noble", "Udemy", "Language Academy"],
        "others": ["General Store", "Miscellaneous"]
    }
    
    expenses = []
    now = datetime.now()
    
    # Create 50 sample expenses over the last 3 months
    for i in range(50):
        # Random date in the last 90 days
        days_ago = random.randint(0, 90)
        expense_date = now - timedelta(days=days_ago)
        
        # Random category
        category = random.choice(categories)
        
        # Merchant based on category
        merchant_list = merchants.get(category.slug, ["Merchant"])
        merchant = random.choice(merchant_list)
        
        # Amount based on category (realistic ranges)
        if category.slug == "food":
            amount = round(random.uniform(5, 80), 2)
        elif category.slug == "transportation":
            amount = round(random.uniform(10, 60), 2)
        elif category.slug == "housing":
            amount = round(random.uniform(30, 150), 2)
        elif category.slug == "health":
            amount = round(random.uniform(15, 100), 2)
        elif category.slug == "leisure":
            amount = round(random.uniform(5, 50), 2)
        elif category.slug == "shopping":
            amount = round(random.uniform(20, 200), 2)
        else:
            amount = round(random.uniform(10, 100), 2)
        
        expense = tables.Expense(
            user_id=user.id,
            date=expense_date,
            merchant=merchant,
            category_id=category.id,
            amount=amount,
            description=f"Expense at {merchant}",
            payment_method=random.choice(["credit_card", "debit_card", "cash"]),
            source="manual"
        )
        
        expenses.append(expense)
        db.add(expense)
    
    db.commit()
    print(f"✅ {len(expenses)} sample expenses created")


def create_sample_budgets(db, user, categories):
    """Creates sample monthly budgets"""
    
    # Typical monthly budget limits
    budget_amounts = {
        "food": 400,
        "transportation": 150,
        "leisure": 100,
        "health": 80
    }
    
    # First day of the current month
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    budgets = []
    for category in categories:
        if category.slug in budget_amounts:
            budget = tables.Budget(
                user_id=user.id,
                category_id=category.id,
                month=current_month,
                amount_limit=budget_amounts[category.slug],
                alert_threshold=0.8
            )
            budgets.append(budget)
            db.add(budget)
    
    db.commit()
    print(f"✅ {len(budgets)} budgets created")


def main():
    """Main execution function"""
    print("🚀 Initializing database...")
    
    # Initialize tables
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if a user already exists
        existing_user = db.query(tables.User).first()
        
        if existing_user:
            print("⚠️ A user already exists. Do you want to create additional sample data? (y/n)")
            response = input().lower()
            if response != 'y':
                print("Cancelled.")
                return
            user = existing_user
        else:
            # Create sample user
            user = create_sample_user(db)
        
        # Create categories
        categories = create_categories(db)
        
        # Create sample expenses
        create_sample_expenses(db, user, categories)
        
        # Create sample budgets
        create_sample_budgets(db, user, categories)
        
        print("\n✅ Database initialized successfully!")
        print(f"📧 Demo User: demo@example.com")
        print(f"📊 Expenses Created: 50")
        print(f"🎯 Budgets Configured")
        print("\n🚀 You can now start the application!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
