import easyocr
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

from backend.config.settings import settings
from backend.utils.image_processing import preprocess_image

logger = logging.getLogger(__name__)


class OCRService:
    """Service for text extraction using OCR"""
    
    def __init__(self):
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initializes the OCR reader"""
        try:
            logger.info(f"Initializing EasyOCR with languages: {settings.ocr_languages}")
            self.reader = easyocr.Reader(
                settings.ocr_languages,
                gpu=False  # Set to True if you have a GPU
            )
            logger.info("✅ EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing EasyOCR: {e}")
            raise
    
    def extract_text(self, image_path: str) -> Dict[str, any]:
        """
        Extracts text from an image
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            # Preprocess image
            processed_image = preprocess_image(image_path)
            
            # Extract text
            results = self.reader.readtext(processed_image)
            
            # Process results
            text_blocks = []
            full_text = []
            total_confidence = 0
            
            for bbox, text, confidence in results:
                text_blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
                full_text.append(text)
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(results) if results else 0
            
            return {
                "success": True,
                "full_text": "\n".join(full_text),
                "text_blocks": text_blocks,
                "confidence": avg_confidence,
                "num_blocks": len(results)
            }
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "full_text": "",
                "text_blocks": [],
                "confidence": 0
            }
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extracts text from a PDF
        
        Args:
            pdf_path: Path to the PDF
            
        Returns:
            Dict with extracted text
        """
        try:
            # Convert PDF to images (requires pdf2image)
            from pdf2image import convert_from_path
            
            images = convert_from_path(pdf_path)
            all_results = []
            
            for i, image in enumerate(images):
                # Save temporarily as image
                temp_path = f"/tmp/pdf_page_{i}.jpg"
                image.save(temp_path, "JPEG")
                
                # Extract text
                result = self.extract_text(temp_path)
                if result["success"]:
                    all_results.append(result)
            
            # Combine results
            combined_text = "\n\n".join([r["full_text"] for r in all_results])
            avg_confidence = np.mean([r["confidence"] for r in all_results]) if all_results else 0
            
            return {
                "success": True,
                "full_text": combined_text,
                "pages": len(all_results),
                "confidence": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                "success": False,
                "error": str(e),
                "full_text": ""
            }
    
    def extract_with_layout(self, image_path: str) -> List[Dict]:
        """
        Extracts text preserving layout/structure
        Useful for receipts where position matters
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of text blocks ordered by position
        """
        try:
            result = self.extract_text(image_path)
            if not result["success"]:
                return []
            
            # Sort blocks by position (top to bottom)
            blocks = result["text_blocks"]
            blocks.sort(key=lambda x: x["bbox"][0][1])  # Sort by Y coordinate
            
            return blocks
            
        except Exception as e:
            logger.error(f"Error in layout extraction: {e}")
            return []
    
    def validate_extraction(self, text: str, min_length: int = 10) -> bool:
        """
        Validates if the text extraction is valid
        
        Args:
            text: Extracted text
            min_length: Minimum expected length
            
        Returns:
            True if the extraction is valid
        """
        if not text or len(text.strip()) < min_length:
            return False
        
        # Check if it contains some numbers (common in receipts)
        has_numbers = any(char.isdigit() for char in text)
        
        return has_numbers


# Global service instance
ocr_service = OCRService()
