"""
Text processing utility functions
"""
import re
from typing import List, Optional
from datetime import datetime
import unicodedata


def clean_text(text: str) -> str:
    """
    Cleans text by removing special characters and normalizing whitespace
    
    Args:
        text: String to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Remove control characters
    text = ''.join(char for char in text if not unicodedata.category(char).startswith('C'))
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def remove_accents(text: str) -> str:
    """
    Removes accents/diacritics from a string
    
    Args:
        text: Text with accents
        
    Returns:
        Text without accents
    """
    if not text:
        return ""
    
    # Normalize and remove diacritic marks
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def normalize_merchant_name(merchant: str) -> str:
    """
    Normalizes a merchant/business name
    
    Args:
        merchant: Raw merchant name
        
    Returns:
        Normalized name
    """
    if not merchant:
        return ""
    
    # Convert to uppercase
    merchant = merchant.upper()
    
    # Clean string
    merchant = clean_text(merchant)
    
    # Remove common corporate suffixes
    stop_words = ['S.L.', 'S.A.', 'SL', 'SA', 'SLU', 'S.L.U.', 'LTD', 'INC', 'CORP', 'LLC']
    for word in stop_words:
        merchant = merchant.replace(word, '')
    
    # Normalize whitespace
    merchant = ' '.join(merchant.split())
    
    return merchant.strip()


def extract_numbers(text: str) -> List[float]:
    """
    Extracts all numbers from a string
    
    Args:
        text: Text to parse
        
    Returns:
        List of found numbers
    """
    if not text:
        return []
    
    # Pattern for numbers (including decimals with . or ,)
    pattern = r'\d+[.,]?\d*'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            # Normalize decimal separator
            num_str = match.replace(',', '.')
            numbers.append(float(num_str))
        except ValueError:
            continue
    
    return numbers


def extract_date_strings(text: str) -> List[str]:
    """
    Extracts strings that resemble dates
    
    Args:
        text: Text to parse
        
    Returns:
        List of potential date strings
    """
    if not text:
        return []
    
    # Common date patterns
    patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',    # YYYY-MM-DD
        r'\w+\s+\d{1,2},?\s+\d{4}',        # Month DD, YYYY
    ]
    
    dates = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return dates


def tokenize(text: str, lowercase: bool = True) -> List[str]:
    """
    Tokenizes text into a list of words
    
    Args:
        text: Text to tokenize
        lowercase: Whether to convert to lowercase
        
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    if lowercase:
        text = text.lower()
    
    # Remove punctuation except hyphens
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Split by whitespace
    tokens = text.split()
    
    return [t for t in tokens if t]


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculates basic Jaccard similarity between two strings
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Tokenize
    tokens1 = set(tokenize(text1))
    tokens2 = set(tokenize(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    
    return len(intersection) / len(union)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncates text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Formats a numeric amount as currency
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, GBP)
        
    Returns:
        Formatted string
    """
    symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£"
    }
    
    symbol = symbols.get(currency, currency)
    
    # Format with thousands separators and 2 decimals
    if currency == "EUR":
        # European format: 1.234,56 €
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} {symbol}"
    else:
        # Standard US/UK format: $1,234.56
        formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extracts keywords from a text string
    
    Args:
        text: Text to parse
        min_length: Minimum word length
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Common English stop words
    stop_words = {
        'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'you', 'that', 'he', 
        'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'at', 'be', 
        'this', 'from', 'i', 'have', 'or', 'by', 'one', 'had', 'not', 'but', 
        'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 
        'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will'
    }
    
    # Tokenize
    tokens = tokenize(text)
    
    # Filter
    keywords = [
        token for token in tokens
        if len(token) >= min_length and token not in stop_words
    ]
    
    # Count frequencies
    from collections import Counter
    freq = Counter(keywords)
    
    # Return most common
    return [word for word, _ in freq.most_common(max_keywords)]


def is_valid_email(email: str) -> bool:
    """
    Validates if a string is a properly formatted email
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by removing dangerous characters
    
    Args:
        filename: Raw filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limit length
    filename = truncate_text(filename, 200, "")
    
    return filename or "unnamed"
