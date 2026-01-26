from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from backend.models.database import get_db
from backend.models import tables, schemas
from backend.config.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=schemas.ExpenseInDB, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db)
):
    """Creates a new expense"""
    try:
        # Validate that the category exists
        category = db.query(tables.Category).filter(
            tables.Category.id == expense.category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
        
        # Create expense
        db_expense = tables.Expense(
            **expense.model_dump(exclude={"user_id"}),
            user_id=1  # TODO: Get from authentication token
        )
        
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        
        logger.info(f"Expense created: ID {db_expense.id}")
        
        return db_expense
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating expense: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["database_error"]
        )


@router.get("/", response_model=List[schemas.ExpenseInDB])
def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of expenses with optional filters
    """
    try:
        # Base Query
        query = db.query(tables.Expense).filter(
            tables.Expense.user_id == 1  # TODO: From token
        )
        
        # Apply filters
        if category_id:
            query = query.filter(tables.Expense.category_id == category_id)
        
        if start_date:
            query = query.filter(tables.Expense.date >= start_date)
        
        if end_date:
            query = query.filter(tables.Expense.date <= end_date)
        
        if min_amount:
            query = query.filter(tables.Expense.amount >= min_amount)
        
        if max_amount:
            query = query.filter(tables.Expense.amount <= max_amount)
        
        if search:
            search_filter = or_(
                tables.Expense.merchant.ilike(f"%{search}%"),
                tables.Expense.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Order by descending date
        query = query.order_by(desc(tables.Expense.date))
        
        # Pagination
        expenses = query.offset(skip).limit(limit).all()
        
        return expenses
        
    except Exception as e:
        logger.error(f"Error retrieving expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{expense_id}", response_model=schemas.ExpenseInDB)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific expense by ID"""
    expense = db.query(tables.Expense).filter(
        and_(
            tables.Expense.id == expense_id,
            tables.Expense.user_id == 1  # TODO: From token
        )
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )
    
    return expense


@router.put("/{expense_id}", response_model=schemas.ExpenseInDB)
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """Updates an existing expense"""
    try:
        db_expense = db.query(tables.Expense).filter(
            and_(
                tables.Expense.id == expense_id,
                tables.Expense.user_id == 1  # TODO: From token
            )
        ).first()
        
        if not db_expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )
        
        # Update fields
        update_data = expense_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_expense, field, value)
        
        db.commit()
        db.refresh(db_expense)
        
        logger.info(f"Expense updated: ID {expense_id}")
        
        return db_expense
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating expense: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Deletes an expense"""
    try:
        db_expense = db.query(tables.Expense).filter(
            and_(
                tables.Expense.id == expense_id,
                tables.Expense.user_id == 1
            )
        ).first()
        
        if not db_expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )
        
        db.delete(db_expense)
        db.commit()
        
        logger.info(f"Expense deleted: ID {expense_id}")
        
        return {
            "success": True,
            "message": SUCCESS_MESSAGES["expense_deleted"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting expense: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/total")
def get_total_expenses(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieves the total expenses with optional filters"""
    
    query = db.query(
        func.sum(tables.Expense.amount).label("total"),
        func.count(tables.Expense.id).label("count")
    ).filter(tables.Expense.user_id == 1)
    
    if start_date:
        query = query.filter(tables.Expense.date >= start_date)
    
    if end_date:
        query = query.filter(tables.Expense.date <= end_date)
    
    if category_id:
        query = query.filter(tables.Expense.category_id == category_id)
    
    result = query.first()
    
    return {
        "total_amount": float(result.total) if result.total else 0.0,
        "total_count": result.count,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "category_id": category_id
        }
    }


@router.get("/recent/latest")
def get_recent_expenses(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Retrieves the most recent expenses"""
    expenses = db.query(tables.Expense).filter(
        tables.Expense.user_id == 1
    ).order_by(
        desc(tables.Expense.date)
    ).limit(limit).all()
    
    return expenses
