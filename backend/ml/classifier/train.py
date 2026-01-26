"""
Training script for expense classifier
"""
import sys
from pathlib import Path
import pickle

# Add root to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
import pandas as pd

from backend.models.database import SessionLocal
from backend.models import tables
from backend.config.constants import EXPENSE_CATEGORIES


def load_training_data():
    """Load training data from database"""
    db = SessionLocal()
    
    try:
        # Fetch all expenses with categories
        expenses = db.query(tables.Expense).join(tables.Category).all()
        
        if not expenses:
            print("⚠️ No expenses found in database")
            return None, None
        
        # Prepare training data
        X = []
        y = []
        
        for expense in expenses:
            # Combine merchant and description
            text = f"{expense.merchant or ''} {expense.description or ''}".strip()
            if text:
                X.append(text.lower())
                y.append(expense.category.slug)
        
        return X, y
        
    finally:
        db.close()


def create_synthetic_data():
    """Create synthetic training data from category keywords"""
    X = []
    y = []
    
    for category_slug, info in EXPENSE_CATEGORIES.items():
        keywords = info["keywords"]
        
        for keyword in keywords:
            # Add keyword as-is
            X.append(keyword.lower())
            y.append(category_slug)
            
            # Add variations
            X.append(f"purchase at {keyword}".lower())
            y.append(category_slug)
            
            X.append(f"{keyword} store".lower())
            y.append(category_slug)
    
    return X, y


def train_classifier():
    """Train the expense classifier"""
    print("🚀 Starting classifier training...")
    
    # Load data from database
    X_db, y_db = load_training_data()
    
    # Create synthetic data
    X_syn, y_syn = create_synthetic_data()
    
    # Combine datasets
    if X_db and y_db:
        X = X_db + X_syn
        y = y_db + y_syn
        print(f"📊 Using {len(X_db)} real + {len(X_syn)} synthetic samples")
    else:
        X = X_syn
        y = y_syn
        print(f"📊 Using {len(X_syn)} synthetic samples (no real data available)")
    
    if len(X) < 10:
        print("❌ Insufficient training data")
        return None
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📈 Training set: {len(X_train)} samples")
    print(f"📊 Test set: {len(X_test)} samples")
    
    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            lowercase=True
        )),
        ('clf', MultinomialNB())
    ])
    
    # Train model
    print("🔄 Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)
    
    print(f"✅ Training accuracy: {train_score:.2%}")
    print(f"✅ Test accuracy: {test_score:.2%}")
    
    # Cross-validation
    print("🔄 Performing cross-validation...")
    cv_scores = cross_val_score(pipeline, X, y, cv=5)
    print(f"✅ Cross-validation: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")
    
    return pipeline


def save_model(model):
    """Save trained model"""
    if model is None:
        print("❌ No model to save")
        return
    
    # Create directory
    model_dir = Path(root_dir) / "backend" / "ml" / "saved_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "classifier.pkl"
    
    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"💾 Model saved to: {model_path}")


def main():
    """Main training function"""
    print("="*60)
    print("EXPENSE CLASSIFIER TRAINING")
    print("="*60)
    print()
    
    # Train
    model = train_classifier()
    
    # Save
    if model:
        save_model(model)
        print()
        print("="*60)
        print("✅ TRAINING COMPLETED SUCCESSFULLY")
        print("="*60)
    else:
        print()
        print("="*60)
        print("❌ TRAINING FAILED")
        print("="*60)


if __name__ == "__main__":
    main()