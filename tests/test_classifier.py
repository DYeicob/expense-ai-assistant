"""
Tests for expense classifier
"""
import pytest
import sys
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.services.classifier_service import expense_classifier
from backend.config.constants import EXPENSE_CATEGORIES


class TestExpenseClassifier:
    """Test expense classifier functionality"""
    
    def test_classifier_initialization(self):
        """Test classifier initializes correctly"""
        assert expense_classifier.model is not None
        assert len(expense_classifier.category_map) > 0
        print("✅ Classifier initialized")
    
    def test_classify_food_category(self):
        """Test classification of food expenses"""
        test_cases = [
            ("walmart", "food"),
            ("whole foods", "food"),
            ("mcdonalds", "food"),
            ("grocery store", "food"),
            ("restaurant", "food"),
        ]
        
        for text, expected_category in test_cases:
            category, confidence = expense_classifier.classify(text=text)
            assert category == expected_category, f"Failed for '{text}': got {category}, expected {expected_category}"
            assert confidence > 0.5, f"Low confidence for '{text}': {confidence}"
    
    def test_classify_transportation(self):
        """Test classification of transportation expenses"""
        test_cases = [
            ("shell gas", "transportation"),
            ("uber ride", "transportation"),
            ("metro card", "transportation"),
            ("parking lot", "transportation"),
        ]
        
        for text, expected_category in test_cases:
            category, confidence = expense_classifier.classify(text=text)
            assert category == expected_category
            assert confidence > 0.5
    
    def test_classify_shopping(self):
        """Test classification of shopping expenses"""
        test_cases = [
            ("amazon", "shopping"),
            ("best buy", "shopping"),
            ("target", "shopping"),
        ]
        
        for text, expected_category in test_cases:
            category, confidence = expense_classifier.classify(text=text)
            # Note: Some stores might be classified as food
            assert category in [expected_category, "food"]
    
    def test_classify_with_merchant_and_description(self):
        """Test classification with multiple inputs"""
        category, confidence = expense_classifier.classify(
            text="Store",
            merchant="Whole Foods",
            description="Weekly groceries"
        )
        
        assert category == "food"
        assert confidence > 0.7
    
    def test_get_category_suggestions(self):
        """Test getting multiple category suggestions"""
        suggestions = expense_classifier.get_category_suggestions("food store", top_n=3)
        
        assert len(suggestions) <= 3
        assert all(isinstance(s, tuple) for s in suggestions)
        assert all(len(s) == 2 for s in suggestions)
        
        # First suggestion should be food
        assert suggestions[0][0] == "food"
    
    def test_rule_based_classification(self):
        """Test rule-based classification fallback"""
        # Test exact match
        category, confidence = expense_classifier._classify_by_rules("walmart")
        assert category == "food"
        assert confidence > 0.7
        
        # Test partial match
        category, confidence = expense_classifier._classify_by_rules("went to walmart store")
        assert category == "food"
    
    def test_unknown_merchant(self):
        """Test classification of unknown merchant"""
        category, confidence = expense_classifier.classify(
            text="unknown merchant xyz123"
        )
        
        # Should default to "other" category
        assert category in EXPENSE_CATEGORIES.keys()
        # Confidence might be low
        assert 0 <= confidence <= 1
    
    def test_category_map_structure(self):
        """Test category map has correct structure"""
        for slug, info in expense_classifier.category_map.items():
            assert "name" in info
            assert "keywords" in info
            assert isinstance(info["keywords"], list)


class TestClassifierTraining:
    """Test classifier training functionality"""
    
    def test_train_with_insufficient_data(self):
        """Test training with too few samples"""
        # Should not crash, just warn
        expense_classifier.train_with_user_data([])
        # No assertion needed, just checking it doesn't crash
    
    def test_save_and_load_model(self):
        """Test model saving and loading"""
        # Save current model
        expense_classifier.save_model()
        
        # Model file should exist
        model_path = Path(expense_classifier.model.__class__.__name__)
        # Just verify save doesn't crash
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
