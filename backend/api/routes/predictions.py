"""
Prediction endpoints for forecasting future expenses
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging
import pandas as pd

from backend.models.database import get_db
from backend.models import tables
from backend.services.prediction_service import prediction_service
from backend.api.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/forecast")
def get_expense_forecast(
    periods: int = Query(3, ge=1, le=12, description="Number of months to forecast"),
    category_id: Optional[int] = Query(None, description="Category to filter by"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get expense forecast for future periods
    
    Args:
        periods: Number of months to predict (1-12)
        category_id: Optional category filter
        db: Database session
        user_id: Current user ID
        
    Returns:
        Predictions with confidence intervals
    """
    try:
        # Fetch historical expenses
        query = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        )
        
        # Filter by category if specified
        if category_id:
            query = query.filter(tables.Expense.category_id == category_id)
        
        expenses = query.all()
        
        if not expenses:
            return {
                "success": False,
                "message": "No expense data found for prediction",
                "predictions": []
            }
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount,
            'category': exp.category.slug
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        
        # Get category filter if specified
        category = None
        if category_id:
            cat = db.query(tables.Category).filter(
                tables.Category.id == category_id
            ).first()
            if cat:
                category = cat.slug
        
        # Generate predictions
        predictions = prediction_service.predict_future_expenses(
            df,
            periods=periods,
            category=category
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/by-category")
def get_forecast_by_category(
    periods: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get expense forecast for each category
    
    Args:
        periods: Number of months to predict
        db: Database session
        user_id: Current user ID
        
    Returns:
        Predictions grouped by category
    """
    try:
        # Fetch all expenses
        expenses = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        ).all()
        
        if not expenses:
            return {
                "success": False,
                "message": "No expense data found",
                "predictions": {}
            }
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount,
            'category': exp.category.slug,
            'category_name': exp.category.name
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        
        # Generate predictions by category
        predictions_by_cat = prediction_service.predict_by_category(
            df,
            periods=periods
        )
        
        return {
            "success": True,
            "periods": periods,
            "predictions": predictions_by_cat
        }
        
    except Exception as e:
        logger.error(f"Error generating category forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend")
def get_spending_trend(
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Detect spending trend (increasing, decreasing, stable)
    
    Args:
        category_id: Optional category filter
        db: Database session
        user_id: Current user ID
        
    Returns:
        Trend information
    """
    try:
        # Fetch expenses
        query = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        )
        
        if category_id:
            query = query.filter(tables.Expense.category_id == category_id)
        
        expenses = query.all()
        
        if len(expenses) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 2 expenses to detect trend"
            }
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        
        # Detect trend
        trend_info = prediction_service.detect_trend(df)
        
        return trend_info
        
    except Exception as e:
        logger.error(f"Error detecting trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
def train_prediction_model(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Train/retrain prediction model with latest data
    
    Args:
        db: Database session
        user_id: Current user ID
        
    Returns:
        Training status
    """
    try:
        # Fetch all user expenses
        expenses = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        ).all()
        
        if not expenses:
            raise HTTPException(
                status_code=400,
                detail="No expense data available for training"
            )
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount,
            'category': exp.category.slug
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        
        # Train model
        prediction_service.train_with_data(df)
        
        return {
            "success": True,
            "message": "Model trained successfully",
            "training_samples": len(expenses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accuracy")
def get_model_accuracy(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get prediction model accuracy metrics
    
    Args:
        db: Database session
        user_id: Current user ID
        
    Returns:
        Model accuracy information
    """
    try:
        # Fetch expenses
        expenses = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        ).all()
        
        if not expenses:
            return {
                "success": False,
                "message": "No data available"
            }
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get monthly aggregation
        monthly_data = df.groupby(
            pd.Grouper(key='date', freq='M')
        )['amount'].sum().reset_index()
        
        if len(monthly_data) < 3:
            return {
                "success": False,
                "message": "Insufficient data for accuracy calculation"
            }
        
        # Simple accuracy calculation
        import numpy as np
        monthly_data['month_num'] = range(len(monthly_data))
        X = monthly_data[['month_num']].values
        y = monthly_data['amount'].values
        
        # Fit model
        prediction_service.model.fit(X, y)
        predictions = prediction_service.model.predict(X)
        
        # Calculate R²
        r_squared = prediction_service.model.score(X, y)
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((y - predictions) ** 2))
        
        return {
            "success": True,
            "metrics": {
                "r_squared": float(r_squared),
                "rmse": float(rmse),
                "training_samples": len(monthly_data),
                "model_type": "Linear Regression"
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
def get_budget_recommendations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get budget recommendations based on predictions
    
    Args:
        db: Database session
        user_id: Current user ID
        
    Returns:
        Budget recommendations
    """
    try:
        # Fetch expenses
        expenses = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        ).all()
        
        if not expenses:
            return {
                "success": False,
                "message": "No data available for recommendations"
            }
        
        # Convert to DataFrame
        data = [{
            'date': exp.date,
            'amount': exp.amount,
            'category': exp.category.name
        } for exp in expenses]
        
        df = pd.DataFrame(data)
        
        # Calculate average spending by category
        category_avg = df.groupby('category')['amount'].mean().sort_values(ascending=False)
        
        # Generate recommendations
        recommendations = []
        
        for category, avg in category_avg.head(5).items():
            # Suggest budget as 110% of average (with buffer)
            suggested_budget = avg * 1.1
            
            recommendations.append({
                "category": category,
                "current_average": float(avg),
                "suggested_budget": float(suggested_budget),
                "reason": f"Based on average spending of ${avg:.2f}"
            })
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))