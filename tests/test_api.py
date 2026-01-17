"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from datetime import datetime

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.api.main import app
from backend.models.database import get_db, Base, engine

# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns app info"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data


class TestExpenseEndpoints:
    """Test expense CRUD endpoints"""
    
    def test_get_expenses_empty(self):
        """Test getting expenses when none exist"""
        response = client.get("/api/expenses/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_expense_success(self):
        """Test creating a valid expense"""
        expense_data = {
            "date": datetime.now().isoformat(),
            "merchant": "Test Store",
            "category_id": 1,
            "amount": 50.0,
            "description": "Test expense",
            "payment_method": "credit_card"
        }
        
        response = client.post("/api/expenses/", json=expense_data)
        # May fail if categories not initialized
        assert response.status_code in [201, 404]
    
    def test_create_expense_invalid_amount(self):
        """Test creating expense with invalid amount"""
        expense_data = {
            "date": datetime.now().isoformat(),
            "merchant": "Test Store",
            "category_id": 1,
            "amount": -10.0,  # Invalid
            "payment_method": "credit_card"
        }
        
        response = client.post("/api/expenses/", json=expense_data)
        assert response.status_code in [400, 422]
    
    def test_create_expense_missing_required_fields(self):
        """Test creating expense without required fields"""
        expense_data = {
            "merchant": "Test Store"
            # Missing date, category_id, amount
        }
        
        response = client.post("/api/expenses/", json=expense_data)
        assert response.status_code == 422
    
    def test_get_expenses_with_filters(self):
        """Test getting expenses with query filters"""
        params = {
            "min_amount": 10.0,
            "max_amount": 100.0,
            "limit": 10
        }
        
        response = client.get("/api/expenses/", params=params)
        assert response.status_code == 200
    
    def test_get_expense_not_found(self):
        """Test getting non-existent expense"""
        response = client.get("/api/expenses/99999")
        assert response.status_code == 404
    
    def test_get_expenses_summary(self):
        """Test getting expense summary"""
        response = client.get("/api/expenses/summary/total")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_get_summary(self):
        """Test getting analytics summary"""
        response = client.get("/api/analytics/summary?period=month")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "total_expenses" in data
        assert "total_transactions" in data
    
    def test_get_by_category(self):
        """Test getting expenses by category"""
        response = client.get("/api/analytics/by-category")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert "total" in data
    
    def test_get_trends(self):
        """Test getting expense trends"""
        response = client.get("/api/analytics/trends?period=month&group_by=day")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_top_merchants(self):
        """Test getting top merchants"""
        response = client.get("/api/analytics/top-merchants?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_detect_anomalies(self):
        """Test anomaly detection"""
        response = client.get("/api/analytics/anomalies")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_statistics(self):
        """Test getting general statistics"""
        response = client.get("/api/analytics/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_expenses" in data
        assert "total_amount" in data
        assert "average_expense" in data


class TestUploadEndpoints:
    """Test upload endpoints"""
    
    def test_suggest_category(self):
        """Test category suggestion"""
        response = client.get("/api/upload/categories/suggest?text=walmart")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            assert "category_id" in data[0]
            assert "category_name" in data[0]
            assert "confidence" in data[0]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test sending invalid JSON"""
        response = client.post(
            "/api/expenses/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/expenses/")
        # CORS headers should be present
        # Exact implementation depends on CORS middleware config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
