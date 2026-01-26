"""
Shared dependencies for FastAPI routes
"""
from typing import Optional
from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.models.database import SessionLocal


def get_db():
    """
    Database session dependency
    
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Get current user ID from authorization header
    
    Args:
        authorization: Authorization header (Bearer token)
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If authorization is invalid
        
    Note:
        Currently returns a default user ID (1) for development.
        In production, this should validate JWT tokens and return actual user ID.
    """
    # TODO: Implement JWT token validation
    # For now, return default user ID for development
    return 1


def verify_api_key(
    x_api_key: Optional[str] = Header(None)
) -> bool:
    """
    Verify API key for external integrations
    
    Args:
        x_api_key: API key from header
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If API key is invalid
        
    Note:
        This is for future API key authentication
    """
    # TODO: Implement API key validation
    # For now, accept all requests
    return True


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Get pagination parameters with validation
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Dictionary with validated pagination params
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000"
        )
    
    return {"skip": skip, "limit": limit}


def check_admin_permission(
    user_id: int = None
) -> bool:
    """
    Check if user has admin permissions
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user is admin
        
    Raises:
        HTTPException: If user doesn't have permission
        
    Note:
        Currently not implemented - for future use
    """
    # TODO: Implement admin permission check
    return True


def validate_file_upload(
    file_size: int,
    file_type: str,
    max_size: int = 10 * 1024 * 1024  # 10MB
) -> bool:
    """
    Validate uploaded file
    
    Args:
        file_size: Size of file in bytes
        file_type: MIME type of file
        max_size: Maximum allowed size
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check file size
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
        )
    
    # Check file type
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf"
    ]
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type {file_type} not supported. Allowed: JPG, PNG, PDF"
        )
    
    return True


def get_date_range_params(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Parse and validate date range parameters
    
    Args:
        start_date: Start date string (ISO format)
        end_date: End date string (ISO format)
        
    Returns:
        Tuple of (start_date, end_date) as datetime objects
        
    Raises:
        HTTPException: If dates are invalid
    """
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Validate that start is before end
        if start and end and start > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        return start, end
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format. Use ISO format (YYYY-MM-DD): {str(e)}"
        )