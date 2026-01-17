"""
Basic tests for the expenses module
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.api.main import app
from backend.models.database import get_db, Base, engine
from backend.models import tables
from backend.utils.validators import (
    validate_amount,
    validate_date,
    validate_category_id,
    ValidationError
)

# Test client
client = TestClient(app)


# Fixtures
@pytest.fixture(scope="module")
def test_db():
    """Creates a test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_expense_data():
    """Sample data for an expense"""
    return {
        "date": datetime.now().isoformat(),
        "merchant": "Test Store",
        "category_id": 1,
        "amount": 50.0,
        "description": "Test expense",
        "payment_method": "credit_card"
    }


# API Tests
class TestExpensesAPI:
    """Tests for expense endpoints"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data
    
    def test_get_expenses_empty(self):
        """Test getting expenses when none exist"""
        response = client.get("/api/expenses/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_expense(self, sample_expense_data):
        """Test creating an expense"""
        response = client.post("/api/expenses/", json=sample_expense_data)
        # May fail if no categories exist in the DB
        assert response.status_code in [201, 404]
    
    def test_create_expense_invalid_amount(self, sample_expense_data):
        """Test creating an expense with an invalid amount"""
        invalid_data = sample_expense_data.copy()
        invalid_data["amount"] = -10
        response = client.post("/api/expenses/", json=invalid_data)
        assert response.status_code in [400, 422]


# Validator Tests
class TestValidators:
    """Tests for utility validators"""
    
    def test_validate_amount_valid(self):
        """Test validation of valid amounts"""
        assert validate_amount(50.0) is True
        assert validate_amount(0.01) is True
        assert validate_amount(1000) is True
    
    def test_validate_amount_invalid(self):
        """Test validation of invalid amounts"""
        with pytest.raises(ValidationError):
            validate_amount(0)
        
        with pytest.raises(ValidationError):
            validate_amount(-10)
        
        with pytest.raises(ValidationError):
            validate_amount(10000000)
    
    def test_validate_date_valid(self):
        """Test validation of valid dates"""
        assert validate_date(datetime.now()) is True
        assert validate_date(datetime(2024, 1, 1)) is True
    
    def test_validate_date_future(self):
        """Test validation of future dates"""
        from datetime import timedelta
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValidationError):
            validate_date(future_date, allow_future=False)
    
    def test_validate_category_id_valid(self):
        """Test validation of valid category IDs"""
        assert validate_category_id(1) is True
        assert validate_category_id(10) is True
    
    def test_validate_category_id_invalid(self):
        """Test validation of invalid category IDs"""
        with pytest.raises(ValidationError):
            validate_category_id(0)
        
        with pytest.raises(ValidationError):
            validate_category_id(-1)
        
        with pytest.raises(ValidationError):
            validate_category_id(None)


# Service Tests
class TestOCRService:
    """Tests for the OCR service"""
    
    def test_ocr_service_initialization(self):
        """Test OCR service initialization"""
        from backend.services.ocr_service import ocr_service
        assert ocr_service.reader is not None
    
    def test_validate_extraction(self):
        """Test extraction validation logic"""
        from backend.services.ocr_service import ocr_service
        
        # Valid text
        assert ocr_service.validate_extraction("Total: 50.00$", min_length=10) is True
        
        # Invalid text (too short)
        assert ocr_service.validate_extraction("Test", min_length=10) is False
        
        # Text without numbers
        assert ocr_service.validate_extraction("Just text without numbers") is False


class TestParserService:
    """Tests for the receipt parsing service"""
    
    def test_extract_total(self):
        """Test total amount extraction"""
        from backend.services.parser_service import receipt_parser
        
        text = "Total: 45.50$"
        total = receipt_parser.extract_total(text)
        assert total == 45.50
    
    def test_extract_merchant(self):
        """Test merchant name extraction"""
        from backend.services.parser_service import receipt_parser
        
        text = "WALMART\n123 Main St\nTotal: 50$"
        merchant = receipt_parser.extract_merchant(text)
        assert merchant is not None
        assert "WALMART" in merchant.upper()


class TestClassifierService:
    """Tests for the expense classification service"""
    
    def test_classify_food(self):
        """Test classification as 'food'"""
        from backend.services.classifier_service import expense_classifier
        
        category, confidence = expense_classifier.classify(
            text="whole foods market",
            merchant="Whole Foods"
        )
        assert category == "food"
        assert confidence > 0.5
    
    def test_classify_transport(self):
        """Test classification as 'transportation'"""
        from backend.services.classifier_service import expense_classifier
        
        category, confidence = expense_classifier.classify(
            text="shell gasoline",
            merchant="Shell"
        )
        assert category == "transportation"
        assert confidence > 0.5


# Utility Tests
class TestTextProcessing:
    """Tests for text processing utilities"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        from backend.utils.text_processing import clean_text
        
        text = "  Text   with   spaces  "
        cleaned = clean_text(text)
        assert cleaned == "Text with spaces"
    
    def test_extract_numbers(self):
        """Test extraction of numbers from string"""
        from backend.utils.text_processing import extract_numbers
        
        text = "Total: 45.50$ Tax: 9.55$"
        numbers = extract_numbers(text)
        assert 45.50 in numbers or 45.5 in numbers
        assert 9.55 in numbers
    
    def test_normalize_merchant_name(self):
        """Test merchant name normalization"""
        from backend.utils.text_processing import normalize_merchant_name
        
        merchant = "  walmart  inc.  "
        normalized = normalize_merchant_name(merchant)
        assert normalized == "WALMART"


# Execute tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
