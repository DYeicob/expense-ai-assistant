"""
Tests for OCR service
"""
import pytest
import sys
from pathlib import Path
import cv2
import numpy as np

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.services.ocr_service import ocr_service
from backend.utils.image_processing import preprocess_image


class TestOCRService:
    """Test OCR service functionality"""
    
    def test_ocr_service_initialization(self):
        """Test OCR service initializes correctly"""
        assert ocr_service.reader is not None
        print("✅ OCR service initialized")
    
    def test_validate_extraction_valid(self):
        """Test validation of valid text extraction"""
        text = "Total: $50.00\nDate: 01/15/2024"
        assert ocr_service.validate_extraction(text, min_length=10) is True
    
    def test_validate_extraction_too_short(self):
        """Test validation fails for too short text"""
        text = "Test"
        assert ocr_service.validate_extraction(text, min_length=10) is False
    
    def test_validate_extraction_no_numbers(self):
        """Test validation fails for text without numbers"""
        text = "This is just text without any digits"
        assert ocr_service.validate_extraction(text) is False
    
    def test_extract_text_structure(self):
        """Test extract_text returns correct structure"""
        # Create a simple test image with text
        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, "TEST RECEIPT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Save temporarily
        test_path = "/tmp/test_receipt.jpg"
        cv2.imwrite(test_path, img)
        
        result = ocr_service.extract_text(test_path)
        
        assert "success" in result
        assert "full_text" in result
        assert "text_blocks" in result
        assert "confidence" in result
    
    def test_extract_with_layout(self):
        """Test layout preservation in extraction"""
        # Create test image
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        cv2.putText(img, "Line 1", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, "Line 2", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        test_path = "/tmp/test_layout.jpg"
        cv2.imwrite(test_path, img)
        
        blocks = ocr_service.extract_with_layout(test_path)
        
        assert isinstance(blocks, list)


class TestImageProcessing:
    """Test image processing utilities"""
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create test image
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        test_path = "/tmp/test_preprocess.jpg"
        cv2.imwrite(test_path, img)
        
        processed = preprocess_image(test_path)
        
        assert processed is not None
        assert len(processed.shape) == 2  # Should be grayscale
    
    def test_preprocess_with_target_size(self):
        """Test preprocessing with target size"""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        test_path = "/tmp/test_resize.jpg"
        cv2.imwrite(test_path, img)
        
        target_size = (200, 200)
        processed = preprocess_image(test_path, target_size)
        
        assert processed.shape == target_size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
