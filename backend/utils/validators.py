"""
Application Validators
"""
from datetime import datetime, timedelta
from typing import Optional
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_amount(amount: float, min_value: float = 0.01, max_value: float = 1000000) -> bool:
    """
    Validates that an amount is within allowed limits
    
    Args:
        amount: Amount to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If amount is invalid
    """
    if amount is None:
        raise ValidationError("Amount is required")
    
    if not isinstance(amount, (int, float)):
        raise ValidationError("Amount must be a number")
    
    if amount < min_value:
        raise ValidationError(f"Amount must be greater than or equal to {min_value}")
    
    if amount > max_value:
        raise ValidationError(f"Amount must be less than or equal to {max_value}")
    
    return True


def validate_date(
    date: datetime,
    allow_future: bool = False,
    max_past_days: Optional[int] = 365
) -> bool:
    """
    Validates a date object
    
    Args:
        date: Date to validate
        allow_future: Whether future dates are allowed
        max_past_days: Maximum days in the past (None = no limit)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If date is invalid
    """
    if date is None:
        raise ValidationError("Date is required")
    
    if not isinstance(date, datetime):
        raise ValidationError("Date must be a datetime object")
    
    now = datetime.now()
    
    # Check if future
    if not allow_future and date > now:
        raise ValidationError("Date cannot be in the future")
    
    # Check antiquity
    if max_past_days is not None:
        max_date = now - timedelta(days=max_past_days)
        if date < max_date:
            raise ValidationError(f"Date cannot be older than {max_past_days} days")
    
    return True


def validate_category_id(category_id: int) -> bool:
    """
    Validates a category ID
    
    Args:
        category_id: ID to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if category_id is None:
        raise ValidationError("Category is required")
    
    if not isinstance(category_id, int):
        raise ValidationError("Category ID must be an integer")
    
    if category_id <= 0:
        raise ValidationError("Category ID must be positive")
    
    return True


def validate_merchant_name(merchant: str, min_length: int = 2, max_length: int = 255) -> bool:
    """
    Validates a merchant/store name
    
    Args:
        merchant: Name of the merchant
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if merchant is None:
        return True  # Merchant is optional
    
    if not isinstance(merchant, str):
        raise ValidationError("Merchant name must be text")
    
    merchant = merchant.strip()
    
    if len(merchant) < min_length:
        raise ValidationError(f"Merchant name must have at least {min_length} characters")
    
    if len(merchant) > max_length:
        raise ValidationError(f"Merchant name cannot exceed {max_length} characters")
    
    return True


def validate_description(description: str, max_length: int = 1000) -> bool:
    """
    Validates a description string
    
    Args:
        description: Description to validate
        max_length: Maximum allowed length
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if description is None:
        return True  # Optional
    
    if not isinstance(description, str):
        raise ValidationError("Description must be text")
    
    if len(description) > max_length:
        raise ValidationError(f"Description cannot exceed {max_length} characters")
    
    return True


def validate_payment_method(payment_method: str) -> bool:
    """
    Validates a payment method string
    
    Args:
        payment_method: Payment method type
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    valid_methods = [
        "cash",
        "debit_card",
        "credit_card",
        "transfer",
        "paypal",
        "instant_transfer",
        "other"
    ]
    
    if payment_method is None:
        return True  # Optional
    
    if not isinstance(payment_method, str):
        raise ValidationError("Payment method must be text")
    
    if payment_method.lower() not in valid_methods:
        raise ValidationError(
            f"Invalid payment method. Options: {', '.join(valid_methods)}"
        )
    
    return True


def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
    """
    Validates file size in bytes
    
    Args:
        file_size: Size in bytes
        max_size: Maximum allowed size (default 10MB)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If file is too large
    """
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(f"File cannot exceed {max_mb:.1f}MB")
    
    return True


def validate_file_extension(filename: str, allowed_extensions: list = None) -> bool:
    """
    Validates file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If extension is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ["jpg", "jpeg", "png", "pdf"]
    
    if not filename:
        raise ValidationError("Filename is required")
    
    # Get extension
    ext = filename.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid extension. Allowed: {', '.join(allowed_extensions)}"
        )
    
    return True


def validate_confidence_score(confidence: float) -> bool:
    """
    Validates an AI confidence score
    
    Args:
        confidence: Score between 0 and 1
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if confidence is None:
        return True  # Optional
    
    if not isinstance(confidence, (int, float)):
        raise ValidationError("Confidence must be a number")
    
    if confidence < 0 or confidence > 1:
        raise ValidationError("Confidence must be between 0 and 1")
    
    return True


def validate_email(email: str) -> bool:
    """
    Validates an email address
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if not email:
        raise ValidationError("Email is required")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    return True


def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Validates a password for security requirements
    
    Args:
        password: Password to validate
        min_length: Minimum length
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if not password:
        raise ValidationError("Password is required")
    
    if len(password) < min_length:
        raise ValidationError(f"Password must have at least {min_length} characters")
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        raise ValidationError("Password must contain both letters and numbers")
    
    return True


class ExpenseValidator:
    """Complete validator for expense objects"""
    
    @staticmethod
    def validate_expense_data(expense_data: dict) -> bool:
        """
        Validates all fields in an expense data dictionary
        
        Args:
            expense_data: Dictionary with expense data
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If any data point is invalid
        """
        # Validate required fields
        if 'date' in expense_data:
            validate_date(expense_data['date'])
        
        if 'category_id' in expense_data:
            validate_category_id(expense_data['category_id'])
        
        if 'amount' in expense_data:
            validate_amount(expense_data['amount'])
        
        # Validate optional fields
        if 'merchant' in expense_data and expense_data['merchant']:
            validate_merchant_name(expense_data['merchant'])
        
        if 'description' in expense_data and expense_data['description']:
            validate_description(expense_data['description'])
        
        if 'payment_method' in expense_data and expense_data['payment_method']:
            validate_payment_method(expense_data['payment_method'])
        
        if 'confidence' in expense_data and expense_data['confidence']:
            validate_confidence_score(expense_data['confidence'])
        
        return True
