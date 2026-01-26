"""
Expense classifier model definition
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from typing import Tuple, List


class ExpenseClassifierModel:
    """Expense classification model"""
    
    def __init__(self, model_type: str = "naive_bayes"):
        """
        Initialize classifier model
        
        Args:
            model_type: Type of model ("naive_bayes" or "random_forest")
        """
        self.model_type = model_type
        self.pipeline = self._create_pipeline()
    
    def _create_pipeline(self) -> Pipeline:
        """Create sklearn pipeline with vectorizer and classifier"""
        
        # Vectorizer (common for all models)
        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            lowercase=True,
            min_df=1,
            max_df=0.95
        )
        
        # Choose classifier
        if self.model_type == "random_forest":
            classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        else:  # Default to Naive Bayes
            classifier = MultinomialNB(alpha=1.0)
        
        # Create pipeline
        pipeline = Pipeline([
            ('tfidf', vectorizer),
            ('classifier', classifier)
        ])
        
        return pipeline
    
    def fit(self, X: List[str], y: List[str]):
        """
        Train the model
        
        Args:
            X: List of text samples
            y: List of category labels
        """
        self.pipeline.fit(X, y)
    
    def predict(self, X: List[str]) -> List[str]:
        """
        Predict categories for samples
        
        Args:
            X: List of text samples
            
        Returns:
            List of predicted categories
        """
        return self.pipeline.predict(X)
    
    def predict_proba(self, X: List[str]):
        """
        Predict probabilities for each category
        
        Args:
            X: List of text samples
            
        Returns:
            Array of probabilities
        """
        return self.pipeline.predict_proba(X)
    
    def score(self, X: List[str], y: List[str]) -> float:
        """
        Calculate accuracy score
        
        Args:
            X: List of text samples
            y: True labels
            
        Returns:
            Accuracy score (0-1)
        """
        return self.pipeline.score(X, y)
    
    def get_feature_importance(self, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Get most important features (words)
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            List of (feature, importance) tuples
        """
        if self.model_type != "random_forest":
            return []
        
        # Get feature names
        feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
        
        # Get feature importances
        importances = self.pipeline.named_steps['classifier'].feature_importances_
        
        # Sort by importance
        indices = importances.argsort()[-top_n:][::-1]
        
        return [(feature_names[i], importances[i]) for i in indices]
    
    def get_model_info(self) -> dict:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            "model_type": self.model_type,
            "vectorizer": "TF-IDF",
            "max_features": 500,
            "ngram_range": "(1, 2)",
            "classifier": str(type(self.pipeline.named_steps['classifier']).__name__)
        }


def create_default_model() -> ExpenseClassifierModel:
    """
    Create default classifier model
    
    Returns:
        ExpenseClassifierModel instance
    """
    return ExpenseClassifierModel(model_type="naive_bayes")


def create_advanced_model() -> ExpenseClassifierModel:
    """
    Create advanced classifier model with Random Forest
    
    Returns:
        ExpenseClassifierModel instance
    """
    return ExpenseClassifierModel(model_type="random_forest")