import pickle
import os
from typing import Dict, Tuple, Optional, List
import logging
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

from backend.config.settings import settings
from backend.config.constants import EXPENSE_CATEGORIES

logger = logging.getLogger(__name__)


class ExpenseClassifier:
    """Service for automatically classifying expenses"""
    
    def __init__(self):
        self.model = None
        self.category_map = {}
        self._build_category_map()
        self._load_or_create_model()
    
    def _build_category_map(self):
        """Builds the category mapping"""
        for slug, info in EXPENSE_CATEGORIES.items():
            self.category_map[slug] = {
                "name": info["name"],
                "keywords": info["keywords"]
            }
    
    def _load_or_create_model(self):
        """Loads the model or creates a new one if it doesn't exist"""
        model_path = settings.classifier_model_path
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"✅ Classification model loaded from {model_path}")
            except Exception as e:
                logger.error(f"❌ Error loading model: {e}")
                self._create_default_model()
        else:
            logger.info("Pre-trained model not found, creating base model...")
            self._create_default_model()
    
    def _create_default_model(self):
        """Creates a basic model using category keywords"""
        # Create pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                lowercase=True
            )),
            ('clf', MultinomialNB())
        ])
        
        # Basic training data using keywords
        X_train = []
        y_train = []
        
        for category, info in self.category_map.items():
            keywords = info["keywords"]
            # Create synthetic samples
            for keyword in keywords:
                X_train.append(keyword)
                y_train.append(category)
                # Variations
                X_train.append(f"purchase at {keyword}")
                y_train.append(category)
        
        # Train basic model
        if X_train:
            self.model.fit(X_train, y_train)
            logger.info("✅ Basic model created with keywords")
    
    def classify(
        self, 
        text: str, 
        merchant: Optional[str] = None,
        description: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Classifies an expense into a category
        
        Args:
            text: Main text (can be merchant name)
            merchant: Merchant name (optional)
            description: Expense description (optional)
            
        Returns:
            Tuple of (category, confidence)
        """
        # Combine all available information
        combined_text = " ".join(filter(None, [text, merchant, description]))
        combined_text = combined_text.lower()
        
        # First attempt rule-based classification (more reliable for specific keywords)
        rule_based = self._classify_by_rules(combined_text)
        if rule_based[1] > 0.8:  # High confidence
            return rule_based
        
        # If no high confidence from rules, use ML
        if self.model:
            try:
                prediction = self.model.predict([combined_text])[0]
                probabilities = self.model.predict_proba([combined_text])[0]
                confidence = max(probabilities)
                
                # If ML also has low confidence, default back to rules if they exist
                if confidence < 0.5 and rule_based[1] > 0:
                    return rule_based
                
                return prediction, confidence
            except Exception as e:
                logger.error(f"ML classification error: {e}")
                return rule_based if rule_based[1] > 0 else ("others", 0.3)
        
        # Fallback
        return rule_based if rule_based[1] > 0 else ("others", 0.3)
    
    def _classify_by_rules(self, text: str) -> Tuple[str, float]:
        """
        Rule and keyword based classification
        
        Args:
            text: Text to classify
            
        Returns:
            Tuple of (category, confidence)
        """
        text = text.lower()
        best_category = None
        max_matches = 0
        
        for category, info in self.category_map.items():
            matches = 0
            keywords = info["keywords"]
            
            for keyword in keywords:
                if keyword.lower() in text:
                    # Higher weight if the keyword is the full text
                    if keyword.lower() == text.strip():
                        matches += 3
                    else:
                        matches += 1
            
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        if best_category and max_matches > 0:
            # Confidence based on number of matches
            confidence = min(0.5 + (max_matches * 0.2), 1.0)
            return best_category, confidence
        
        return "others", 0.0
    
    def train_with_user_data(self, expenses: list):
        """
        Re-trains the model with real user data
        
        Args:
            expenses: List of expenses with confirmed categories
        """
        if not expenses or len(expenses) < 10:
            logger.warning("Insufficient data for re-training (minimum 10 samples required)")
            return
        
        X = []
        y = []
        
        for expense in expenses:
            # Combine information
            text = " ".join(filter(None, [
                expense.merchant,
                expense.description
            ]))
            
            if text.strip():
                X.append(text.lower())
                y.append(expense.category.slug)
        
        if len(X) >= 10:
            try:
                # Re-train model
                self.model.fit(X, y)
                
                # Save updated model
                self.save_model()
                
                logger.info(f"✅ Model re-trained with {len(X)} samples")
            except Exception as e:
                logger.error(f"Error re-training model: {e}")
    
    def save_model(self):
        """Saves the trained model"""
        try:
            model_path = settings.classifier_model_path
            
            # Create directory if it doesn't exist
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logger.info(f"✅ Model saved at {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def get_category_suggestions(self, text: str, top_n: int = 3) -> List[Tuple]:
        """
        Gets the top N most likely categories
        
        Args:
            text: Text to classify
            top_n: Number of suggestions
            
        Returns:
            List of (category, confidence)
        """
        text = text.lower()
        suggestions = []
        
        if self.model:
            try:
                probabilities = self.model.predict_proba([text])[0]
                classes = self.model.classes_
                
                # Sort by probability
                indices = np.argsort(probabilities)[::-1][:top_n]
                
                for idx in indices:
                    category = classes[idx]
                    confidence = probabilities[idx]
                    suggestions.append((category, confidence))
                
                return suggestions
            except Exception as e:
                logger.error(f"Error generating suggestions: {e}")
        
        # Fallback with rule-based classification
        category, confidence = self._classify_by_rules(text)
        return [(category, confidence)]


# Global classifier instance
expense_classifier = ExpenseClassifier()
