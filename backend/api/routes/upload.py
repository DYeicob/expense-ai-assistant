from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import logging
from datetime import datetime
import os

from backend.models.database import get_db
from backend.models import tables, schemas
from backend.services.ocr_service import ocr_service
from backend.services.parser_service import receipt_parser
from backend.services.classifier_service import expense_classifier
from backend.config.settings import settings
from backend.config.constants import ERROR_MESSAGES

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_file(file: UploadFile) -> bool:
    """Validates the uploaded file"""
    # Check extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=ERROR_MESSAGES["invalid_format"]
        )
    
    return True


def save_upload_file(file: UploadFile) -> str:
    """Saves the uploaded file and returns the path"""
    # Create unique name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(settings.upload_dir, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return filepath


@router.post("/receipt", response_model=schemas.UploadReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    auto_save: bool = Form(default=False),
    db: Session = Depends(get_db)
):
    """
    Uploads a receipt image, extracts information, and optionally saves the expense
    
    Args:
        file: Image file (JPG, PNG) or PDF
        auto_save: If True, automatically saves the expense to the database
    """
    try:
        # Validate file
        validate_file(file)
        
        # Save file
        filepath = save_upload_file(file)
        logger.info(f"File saved: {filepath}")
        
        # Extract text with OCR
        ext = file.filename.split('.')[-1].lower()
        
        if ext == 'pdf':
            ocr_result = ocr_service.extract_from_pdf(filepath)
        else:
            ocr_result = ocr_service.extract_text(filepath)
        
        if not ocr_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES["ocr_failed"]
            )
        
        # Parse receipt information
        parsed_data = receipt_parser.parse_receipt(ocr_result["full_text"])
        
        # Validate parsed data
        if not receipt_parser.validate_parsed_data(parsed_data):
            raise HTTPException(
                status_code=400,
                detail="Could not extract valid information from the receipt"
            )
        
        # Classify category
        category_slug, classification_confidence = expense_classifier.classify(
            text=parsed_data.get("merchant", ""),
            merchant=parsed_data.get("merchant"),
            description=" ".join([item["description"] for item in parsed_data.get("items", [])])
        )
        
        # Get category ID
        category = db.query(tables.Category).filter(
            tables.Category.slug == category_slug
        ).first()
        
        # Calculate global confidence
        parsing_confidence = receipt_parser.calculate_confidence(parsed_data)
        global_confidence = (ocr_result["confidence"] + parsing_confidence + classification_confidence) / 3
        
        # Prepare OCR response
        ocr_response = schemas.OCRResult(
            text=ocr_result["full_text"],
            date=parsed_data.get("date"),
            merchant=parsed_data.get("merchant"),
            amount=parsed_data.get("total"),
            category_id=category.id if category else None,
            confidence=global_confidence,
            raw_data={
                "items": parsed_data.get("items", []),
                "payment_method": parsed_data.get("payment_method"),
                "ocr_blocks": ocr_result.get("text_blocks", [])
            }
        )
        
        expense_id = None
        
        # If auto_save is enabled, save the expense
        if auto_save and parsed_data.get("total"):
            try:
                expense = tables.Expense(
                    user_id=1,  # TODO: Get from token
                    date=parsed_data.get("date") or datetime.now(),
                    merchant=parsed_data.get("merchant"),
                    category_id=category.id if category else 1,
                    amount=parsed_data.get("total"),
                    description=f"Items: {len(parsed_data.get('items', []))}",
                    payment_method=parsed_data.get("payment_method"),
                    source="ocr",
                    image_path=filepath,
                    confidence=global_confidence,
                    metadata=parsed_data
                )
                
                db.add(expense)
                db.commit()
                db.refresh(expense)
                
                expense_id = expense.id
                logger.info(f"Expense automatically saved: ID {expense_id}")
                
            except Exception as e:
                logger.error(f"Error automatically saving expense: {e}")
                db.rollback()
        
        return schemas.UploadReceiptResponse(
            success=True,
            message="Receipt processed successfully",
            ocr_result=ocr_response,
            expense_id=expense_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing the receipt: {str(e)}"
        )


@router.post("/manual-expense")
async def create_expense_from_ocr(
    ocr_data: schemas.OCRResult,
    db: Session = Depends(get_db)
):
    """
    Creates an expense manually from OCR data confirmed/edited by the user
    """
    try:
        if not ocr_data.amount or ocr_data.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )
        
        expense = tables.Expense(
            user_id=1,  # TODO: From token
            date=ocr_data.date or datetime.now(),
            merchant=ocr_data.merchant,
            category_id=ocr_data.category_id,
            amount=ocr_data.amount,
            source="ocr",
            confidence=ocr_data.confidence,
            metadata=ocr_data.raw_data
        )
        
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        return {
            "success": True,
            "message": "Expense created successfully",
            "expense_id": expense.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating expense from OCR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/suggest")
async def suggest_category(
    text: str,
    db: Session = Depends(get_db)
):
    """
    Suggests categories for a given string of text
    """
    suggestions = expense_classifier.get_category_suggestions(text, top_n=3)
    
    result = []
    for category_slug, confidence in suggestions:
        category = db.query(tables.Category).filter(
            tables.Category.slug == category_slug
        ).first()
        
        if category:
            result.append({
                "category_id": category.id,
                "category_name": category.name,
                "slug": category.slug,
                "confidence": confidence,
                "icon": category.icon
            })
    
    return result
