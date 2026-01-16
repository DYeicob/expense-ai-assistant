import re
from datetime import datetime
from typing import Dict, Optional, List
import logging
from dateutil import parser as date_parser

from backend.config.constants import OCR_PATTERNS

logger = logging.getLogger(__name__)


class ReceiptParser:
    """Service for parsing receipt information"""
    
    def __init__(self):
        self.date_patterns = OCR_PATTERNS["date"]
        self.total_patterns = OCR_PATTERNS["total"]
        self.merchant_patterns = OCR_PATTERNS["merchant"]
    
    def parse_receipt(self, text: str) -> Dict[str, any]:
        """
        Parses the text of a receipt extracting key information
        
        Args:
            text: Text extracted from the receipt
            
        Returns:
            Dict with parsed information
        """
        result = {
            "date": self.extract_date(text),
            "merchant": self.extract_merchant(text),
            "total": self.extract_total(text),
            "items": self.extract_items(text),
            "payment_method": self.extract_payment_method(text),
            "raw_text": text
        }
        
        return result
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """
        Extracts the date from the receipt
        
        Args:
            text: Receipt text
            
        Returns:
            Date as datetime object or None
        """
        # Clean text
        text = text.lower()
        
        # Try specific patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Attempt to parse the date
                    date = date_parser.parse(date_str, dayfirst=True)
                    return date
                except:
                    continue
        
        # Try searching for any date pattern
        # Look for DD/MM/YYYY or DD-MM-YYYY
        general_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        match = re.search(general_pattern, text)
        if match:
            try:
                date = date_parser.parse(match.group(1), dayfirst=True)
                return date
            except:
                pass
        
        logger.warning("Could not extract date from receipt")
        return None
    
    def extract_total(self, text: str) -> Optional[float]:
        """
        Extracts the total amount from the receipt
        
        Args:
            text: Receipt text
            
        Returns:
            Total amount as float or None
        """
        amounts = []
        
        # Search for total patterns
        for pattern in self.total_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1)
                # Clean and convert
                amount_str = amount_str.replace(',', '.')
                try:
                    amount = float(amount_str)
                    amounts.append(amount)
                except:
                    continue
        
        if amounts:
            # Return the highest value (usually the total)
            return max(amounts)
        
        # Search for any number with currency format
        currency_pattern = r'€?\s*(\d+[.,]\d{2})\s*€?'
        matches = re.findall(currency_pattern, text)
        if matches:
            try:
                # Convert all and return the highest
                values = [float(m.replace(',', '.')) for m in matches]
                return max(values)
            except:
                pass
        
        logger.warning("Could not extract total amount from receipt")
        return None
    
    def extract_merchant(self, text: str) -> Optional[str]:
        """
        Extracts the merchant name
        
        Args:
            text: Receipt text
            
        Returns:
            Merchant name or None
        """
        lines = text.split('\n')
        
        # Search in the first few lines (merchant name is usually at the top)
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            
            # Search for uppercase lines (common for merchant names)
            if len(line) > 3 and line.isupper():
                # Clean special characters
                cleaned = re.sub(r'[^A-Z\s]', '', line)
                if len(cleaned) > 3:
                    return cleaned.strip()
            
            # Search for known merchant names
            known_merchants = [
                'mercadona', 'carrefour', 'lidl', 'dia', 'alcampo',
                'eroski', 'aldi', 'hipercor', 'el corte ingles',
                'decathlon', 'media markt', 'fnac', 'ikea', 'zara',
                'mcdonalds', 'burger king', 'telepizza', 'dominos'
            ]
            
            line_lower = line.lower()
            for merchant in known_merchants:
                if merchant in line_lower:
                    return merchant.upper()
        
        # If not found, use the first non-empty line
        for line in lines:
            line = line.strip()
            if len(line) > 3:
                return line[:50]  # Limit length
        
        return None
    
    def extract_items(self, text: str) -> List[Dict[str, any]]:
        """
        Extracts items/products from the receipt
        
        Args:
            text: Receipt text
            
        Returns:
            List of items with description and price
        """
        items = []
        lines = text.split('\n')
        
        # Pattern for lines with item + price
        # Example: "WHOLE MILK              2.50"
        item_pattern = r'^(.+?)\s+(\d+[.,]\d{2})\s*€?$'
        
        for line in lines:
            line = line.strip()
            match = re.match(item_pattern, line)
            
            if match:
                description = match.group(1).strip()
                price_str = match.group(2).replace(',', '.')
                
                try:
                    price = float(price_str)
                    items.append({
                        "description": description,
                        "price": price
                    })
                except:
                    continue
        
        return items
    
    def extract_payment_method(self, text: str) -> Optional[str]:
        """
        Extracts the payment method
        
        Args:
            text: Receipt text
            
        Returns:
            Payment method or None
        """
        text_lower = text.lower()
        
        payment_keywords = {
            "cash": ["efectivo", "cash", "metalico"],
            "card": ["tarjeta", "card", "visa", "mastercard"],
            "debit_card": ["debito", "debit"],
            "credit_card": ["credito", "credit"],
            "bizum": ["bizum"],
            "transfer": ["transferencia", "transfer"]
        }
        
        for method, keywords in payment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return method
        
        return None
    
    def calculate_confidence(self, parsed_data: Dict) -> float:
        """
        Calculates a confidence score based on extracted data
        
        Args:
            parsed_data: Parsed data from the receipt
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.0
        
        # Each found field adds to the confidence
        if parsed_data.get("date"):
            confidence += 0.3
        
        if parsed_data.get("total") and parsed_data["total"] > 0:
            confidence += 0.4
        
        if parsed_data.get("merchant"):
            confidence += 0.2
        
        if parsed_data.get("items"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def validate_parsed_data(self, parsed_data: Dict) -> bool:
        """
        Validates that the parsed data is consistent
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            True if data is valid
        """
        # Must have at least a total
        if not parsed_data.get("total") or parsed_data["total"] <= 0:
            return False
        
        # If it has a date, it must be reasonable (not in the future, not too old)
        if parsed_data.get("date"):
            date = parsed_data["date"]
            now = datetime.now()
            
            # Must not be in the future
            if date > now:
                return False
            
            # Must not be more than 1 year ago (adjustable)
            if (now - date).days > 365:
                logger.warning(f"Date too old: {date}")
                # Do not invalidate, just warn
        
        return True


# Global parser instance
receipt_parser = ReceiptParser()
