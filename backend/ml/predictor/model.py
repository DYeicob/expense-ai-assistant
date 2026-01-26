"""
Expense predictor model definition
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from typing import List, Tuple, Optional


class ExpensePredictorModel:
    """Time series prediction model for expenses"""
    
    def __init__(self, model_type: str = "linear"):
        """
        Initialize predictor model
        
        Args:
            model_type: Type of model ("linear" for now, can extend to ARIMA, Prophet, etc.)
        """
        self.model_type = model_type
        self.model = self._create_model()
        self.is_fitted = False
    
    def _create_model(self):
        """Create the underlying model"""
        if self.model_type == "linear":
            return LinearRegression()
        else:
            # Can add more model types here (ARIMA, Prophet, LSTM, etc.)
            return LinearRegression()
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for training
        
        Args:
            df: DataFrame with 'date' and 'amount' columns
            
        Returns:
            Tuple of (X, y) arrays
        """
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Aggregate by month
        monthly = df.groupby(pd.Grouper(key='date', freq='M'))['amount'].sum().reset_index()
        
        # Create sequential month numbers
        monthly['month_num'] = range(len(monthly))
        
        X = monthly[['month_num']].values
        y = monthly['amount'].values
        
        return X, y
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Train the model
        
        Args:
            X: Feature matrix (month numbers)
            y: Target values (amounts)
        """
        self.model.fit(X, y)
        self.is_fitted = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        predictions = self.model.predict(X)
        # Ensure non-negative predictions
        return np.maximum(predictions, 0)
    
    def predict_future(
        self,
        n_periods: int,
        last_period: int,
        confidence_level: float = 0.95
    ) -> List[dict]:
        """
        Predict future periods with confidence intervals
        
        Args:
            n_periods: Number of periods to predict
            last_period: Last known period number
            confidence_level: Confidence level for intervals
            
        Returns:
            List of predictions with confidence bounds
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Generate future period numbers
        future_periods = np.array([[last_period + i] for i in range(1, n_periods + 1)])
        
        # Make predictions
        predictions = self.predict(future_periods)
        
        # Calculate confidence intervals (simplified approach)
        # In production, use proper statistical methods
        std_error = predictions * 0.1  # 10% standard error (simplified)
        z_score = 1.96 if confidence_level == 0.95 else 2.576
        margin = z_score * std_error
        
        results = []
        for i, pred in enumerate(predictions):
            results.append({
                'period': int(last_period + i + 1),
                'predicted_amount': float(pred),
                'lower_bound': float(max(0, pred - margin[i])),
                'upper_bound': float(pred + margin[i]),
                'confidence': confidence_level
            })
        
        return results
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate R² score
        
        Args:
            X: Feature matrix
            y: True values
            
        Returns:
            R² score
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before scoring")
        
        return self.model.score(X, y)
    
    def get_trend_direction(self) -> str:
        """
        Get trend direction (increasing, decreasing, stable)
        
        Returns:
            Trend direction string
        """
        if not self.is_fitted:
            return "unknown"
        
        # Get coefficient (slope)
        if hasattr(self.model, 'coef_'):
            slope = self.model.coef_[0]
            
            if slope > 10:
                return "increasing"
            elif slope < -10:
                return "decreasing"
            else:
                return "stable"
        
        return "unknown"
    
    def get_model_info(self) -> dict:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        info = {
            "model_type": self.model_type,
            "is_fitted": self.is_fitted,
        }
        
        if self.is_fitted and hasattr(self.model, 'coef_'):
            info["coefficient"] = float(self.model.coef_[0])
            info["intercept"] = float(self.model.intercept_)
            info["trend"] = self.get_trend_direction()
        
        return info


class TimeSeriesFeatureExtractor:
    """Extract features from time series data"""
    
    @staticmethod
    def extract_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract seasonal features (month, quarter, etc.)
        
        Args:
            df: DataFrame with date column
            
        Returns:
            DataFrame with additional features
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    @staticmethod
    def create_lag_features(
        df: pd.DataFrame,
        target_col: str = 'amount',
        lags: List[int] = [1, 2, 3]
    ) -> pd.DataFrame:
        """
        Create lagged features
        
        Args:
            df: DataFrame with target column
            target_col: Column to create lags for
            lags: List of lag periods
            
        Returns:
            DataFrame with lag features
        """
        df = df.copy()
        
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
        
        return df


def create_default_predictor() -> ExpensePredictorModel:
    """
    Create default predictor model
    
    Returns:
        ExpensePredictorModel instance
    """
    return ExpensePredictorModel(model_type="linear")