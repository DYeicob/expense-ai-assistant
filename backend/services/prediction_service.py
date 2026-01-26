"""
Prediction service for forecasting future expenses
"""
import pickle
import os
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from backend.config.settings import settings
from backend.config.constants import PREDICTION_CONFIG

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for predicting future expenses"""
    
    def __init__(self):
        self.model = None
        self.model_path = settings.predictor_model_path
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create a new one"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"✅ Prediction model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"❌ Error loading prediction model: {e}")
                self._create_default_model()
        else:
            logger.info("No prediction model found, creating default...")
            self._create_default_model()
    
    def _create_default_model(self):
        """Create a default linear regression model"""
        self.model = LinearRegression()
        logger.info("✅ Default prediction model created")
    
    def predict_future_expenses(
        self,
        expenses_data: pd.DataFrame,
        periods: int = 3,
        category: Optional[str] = None
    ) -> Dict:
        """
        Predict future expenses for specified periods
        
        Args:
            expenses_data: DataFrame with historical expense data
            periods: Number of future periods to predict (months)
            category: Optional category to filter predictions
            
        Returns:
            Dictionary with predictions and confidence intervals
        """
        try:
            # Validate minimum data requirement
            if len(expenses_data) < PREDICTION_CONFIG["min_data_points"]:
                return {
                    "success": False,
                    "error": f"Insufficient data. Need at least {PREDICTION_CONFIG['min_data_points']} records.",
                    "predictions": []
                }
            
            # Filter by category if specified
            if category:
                expenses_data = expenses_data[expenses_data['category'] == category]
            
            # Prepare time series data
            expenses_data['date'] = pd.to_datetime(expenses_data['date'])
            expenses_data = expenses_data.sort_values('date')
            
            # Aggregate by month
            monthly_data = expenses_data.groupby(
                pd.Grouper(key='date', freq='M')
            )['amount'].sum().reset_index()
            
            # Prepare features (months as numeric)
            monthly_data['month_num'] = range(len(monthly_data))
            X = monthly_data[['month_num']].values
            y = monthly_data['amount'].values
            
            # Train simple linear regression
            self.model.fit(X, y)
            
            # Generate predictions
            last_month = len(monthly_data)
            future_months = np.array([[last_month + i] for i in range(1, periods + 1)])
            predictions = self.model.predict(future_months)
            
            # Calculate confidence intervals (simple approach)
            residuals = y - self.model.predict(X)
            std_error = np.std(residuals)
            confidence = PREDICTION_CONFIG["confidence_interval"]
            z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
            
            margin_of_error = z_score * std_error
            
            # Format results
            results = []
            base_date = monthly_data['date'].max()
            
            for i, pred in enumerate(predictions, 1):
                future_date = base_date + pd.DateOffset(months=i)
                results.append({
                    "month": future_date.strftime("%Y-%m"),
                    "predicted_amount": float(max(0, pred)),  # Ensure non-negative
                    "lower_bound": float(max(0, pred - margin_of_error)),
                    "upper_bound": float(pred + margin_of_error),
                    "confidence": confidence
                })
            
            return {
                "success": True,
                "predictions": results,
                "model_info": {
                    "type": "Linear Regression",
                    "training_samples": len(monthly_data),
                    "r_squared": self.model.score(X, y)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                "success": False,
                "error": str(e),
                "predictions": []
            }
    
    def predict_by_category(
        self,
        expenses_data: pd.DataFrame,
        periods: int = 3
    ) -> Dict[str, Dict]:
        """
        Generate predictions for each category
        
        Args:
            expenses_data: DataFrame with historical expense data
            periods: Number of future periods to predict
            
        Returns:
            Dictionary with predictions per category
        """
        categories = expenses_data['category'].unique()
        predictions_by_category = {}
        
        for category in categories:
            category_pred = self.predict_future_expenses(
                expenses_data,
                periods=periods,
                category=category
            )
            predictions_by_category[category] = category_pred
        
        return predictions_by_category
    
    def detect_trend(self, expenses_data: pd.DataFrame) -> Dict:
        """
        Detect spending trend (increasing, decreasing, stable)
        
        Args:
            expenses_data: DataFrame with historical expense data
            
        Returns:
            Dictionary with trend information
        """
        try:
            # Prepare monthly data
            expenses_data['date'] = pd.to_datetime(expenses_data['date'])
            monthly_data = expenses_data.groupby(
                pd.Grouper(key='date', freq='M')
            )['amount'].sum()
            
            if len(monthly_data) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend using linear regression
            X = np.array(range(len(monthly_data))).reshape(-1, 1)
            y = monthly_data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            
            # Determine trend
            if slope > 10:  # Increasing by more than $10/month
                trend = "increasing"
            elif slope < -10:  # Decreasing by more than $10/month
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "slope": float(slope),
                "description": f"Spending is {trend} by ${abs(slope):.2f} per month"
            }
            
        except Exception as e:
            logger.error(f"Error detecting trend: {e}")
            return {"trend": "error", "error": str(e)}
    
    def save_model(self):
        """Save the trained model"""
        try:
            model_path = Path(self.model_path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logger.info(f"✅ Prediction model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def train_with_data(self, expenses_data: pd.DataFrame):
        """
        Train the prediction model with new data
        
        Args:
            expenses_data: DataFrame with expense data
        """
        try:
            if len(expenses_data) < PREDICTION_CONFIG["min_data_points"]:
                logger.warning(f"Insufficient data for training (need {PREDICTION_CONFIG['min_data_points']})")
                return
            
            # Prepare data
            expenses_data['date'] = pd.to_datetime(expenses_data['date'])
            monthly_data = expenses_data.groupby(
                pd.Grouper(key='date', freq='M')
            )['amount'].sum().reset_index()
            
            monthly_data['month_num'] = range(len(monthly_data))
            X = monthly_data[['month_num']].values
            y = monthly_data['amount'].values
            
            # Train model
            self.model.fit(X, y)
            
            # Save model
            self.save_model()
            
            logger.info(f"✅ Model trained with {len(monthly_data)} months of data")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")


# Global instance
prediction_service = PredictionService()