"""
Training script for expense predictor
"""
import sys
from pathlib import Path
import pickle

# Add root to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from backend.models.database import SessionLocal
from backend.models import tables


def load_expense_data():
    """Load expense data from database"""
    db = SessionLocal()
    
    try:
        # Fetch all expenses
        expenses = db.query(tables.Expense).all()
        
        if not expenses:
            print("⚠️ No expenses found in database")
            return None
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount,
            'category': exp.category.slug
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        return df
        
    finally:
        db.close()


def prepare_time_series_data(df: pd.DataFrame):
    """Prepare data for time series prediction"""
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Aggregate by month
    monthly = df.groupby(pd.Grouper(key='date', freq='M'))['amount'].sum().reset_index()
    
    # Create month number feature
    monthly['month_num'] = range(len(monthly))
    
    return monthly


def train_predictor(df: pd.DataFrame):
    """Train expense predictor model"""
    print("🚀 Starting predictor training...")
    
    if len(df) < 3:
        print("❌ Need at least 3 months of data")
        return None
    
    # Prepare features
    X = df[['month_num']].values
    y = df['amount'].values
    
    print(f"📊 Training with {len(df)} months of data")
    print(f"💰 Amount range: ${y.min():.2f} - ${y.max():.2f}")
    
    # Create model
    model = LinearRegression()
    
    # Train
    print("🔄 Training model...")
    model.fit(X, y)
    
    # Evaluate
    predictions = model.predict(X)
    r2 = r2_score(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    
    print(f"✅ R² Score: {r2:.4f}")
    print(f"✅ RMSE: ${rmse:.2f}")
    
    # Make sample prediction
    next_month = len(df)
    next_pred = model.predict([[next_month]])[0]
    print(f"📈 Next month prediction: ${next_pred:.2f}")
    
    return model


def save_model(model):
    """Save trained predictor model"""
    if model is None:
        print("❌ No model to save")
        return
    
    # Create directory
    model_dir = Path(root_dir) / "backend" / "ml" / "saved_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "predictor.pkl"
    
    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"💾 Model saved to: {model_path}")


def main():
    """Main training function"""
    print("="*60)
    print("EXPENSE PREDICTOR TRAINING")
    print("="*60)
    print()
    
    # Load data
    print("📥 Loading expense data...")
    df = load_expense_data()
    
    if df is None:
        print("❌ No data available")
        return
    
    # Prepare time series
    print("🔄 Preparing time series data...")
    monthly_data = prepare_time_series_data(df)
    
    print(f"📅 Date range: {monthly_data['date'].min()} to {monthly_data['date'].max()}")
    
    # Train
    model = train_predictor(monthly_data)
    
    # Save
    if model:
        save_model(model)
        print()
        print("="*60)
        print("✅ TRAINING COMPLETED SUCCESSFULLY")
        print("="*60)
        print()
        print("💡 Next steps:")
        print("  - Use the model via API: /api/predictions/forecast")
        print("  - Retrain periodically with new data")
    else:
        print()
        print("="*60)
        print("❌ TRAINING FAILED")
        print("="*60)


if __name__ == "__main__":
    main()