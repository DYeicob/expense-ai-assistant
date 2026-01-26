from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from backend.models.database import get_db
from backend.models import tables, schemas
from backend.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary")
async def get_summary(
    period: str = Query("month", regex="^(week|month|quarter|year|all)$"),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de gastos para un período
    
    Args:
        period: week, month, quarter, year, all
        category_id: Filtrar por categoría (opcional)
    """
    return analytics_service.get_period_summary(
        db=db,
        user_id=1,  # TODO: Del token
        period=period,
        category_id=category_id
    )


@router.get("/by-category")
async def get_expenses_by_category(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Agrupa gastos por categoría
    """
    # Fechas por defecto: último mes
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    query = db.query(
        tables.Category.id,
        tables.Category.name,
        tables.Category.icon,
        tables.Category.color,
        func.sum(tables.Expense.amount).label("total"),
        func.count(tables.Expense.id).label("count"),
        func.avg(tables.Expense.amount).label("average")
    ).join(
        tables.Expense
    ).filter(
        and_(
            tables.Expense.user_id == 1,
            tables.Expense.date >= start_date,
            tables.Expense.date <= end_date
        )
    ).group_by(
        tables.Category.id
    ).order_by(
        func.sum(tables.Expense.amount).desc()
    ).all()
    
    # Calcular total general para porcentajes
    total_general = sum([r.total for r in query])
    
    results = []
    for row in query:
        results.append({
            "category_id": row.id,
            "category_name": row.name,
            "icon": row.icon,
            "color": row.color,
            "total_amount": float(row.total),
            "transaction_count": row.count,
            "average_amount": float(row.average),
            "percentage": (float(row.total) / total_general * 100) if total_general > 0 else 0
        })
    
    return {
        "categories": results,
        "total": total_general,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }


@router.get("/trends")
async def get_trends(
    period: str = Query("month", regex="^(week|month|year)$"),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene tendencias de gastos agrupadas por día/semana/mes
    """
    return analytics_service.get_trends(
        db=db,
        user_id=1,
        period=period,
        group_by=group_by,
        category_id=category_id
    )


@router.get("/top-merchants")
async def get_top_merchants(
    limit: int = Query(10, le=50),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene los comercios donde más se gasta
    """
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    query = db.query(
        tables.Expense.merchant,
        func.sum(tables.Expense.amount).label("total"),
        func.count(tables.Expense.id).label("visits"),
        func.avg(tables.Expense.amount).label("average")
    ).filter(
        and_(
            tables.Expense.user_id == 1,
            tables.Expense.merchant.isnot(None),
            tables.Expense.date >= start_date,
            tables.Expense.date <= end_date
        )
    ).group_by(
        tables.Expense.merchant
    ).order_by(
        func.sum(tables.Expense.amount).desc()
    ).limit(limit).all()
    
    return [
        {
            "merchant": row.merchant,
            "total_spent": float(row.total),
            "visit_count": row.visits,
            "average_per_visit": float(row.average)
        }
        for row in query
    ]


@router.get("/monthly-comparison")
async def get_monthly_comparison(
    months: int = Query(6, ge=2, le=12),
    db: Session = Depends(get_db)
):
    """
    Compara gastos mes a mes
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    query = db.query(
        extract('year', tables.Expense.date).label('year'),
        extract('month', tables.Expense.date).label('month'),
        func.sum(tables.Expense.amount).label('total'),
        func.count(tables.Expense.id).label('count')
    ).filter(
        and_(
            tables.Expense.user_id == 1,
            tables.Expense.date >= start_date
        )
    ).group_by(
        'year', 'month'
    ).order_by(
        'year', 'month'
    ).all()
    
    results = []
    for row in query:
        month_name = datetime(int(row.year), int(row.month), 1).strftime('%B %Y')
        results.append({
            "year": int(row.year),
            "month": int(row.month),
            "month_name": month_name,
            "total": float(row.total),
            "count": row.count
        })
    
    return results


@router.get("/anomalies")
async def detect_anomalies(
    threshold: float = Query(3.0, ge=1.0, le=5.0),
    db: Session = Depends(get_db)
):
    """
    Detecta gastos anómalos (fuera de lo normal)
    """
    return analytics_service.detect_anomalies(
        db=db,
        user_id=1,
        threshold=threshold
    )


@router.get("/budget-status")
async def get_budget_status(
    month: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de los presupuestos configurados
    """
    if not month:
        month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener presupuestos del mes
    budgets = db.query(tables.Budget).filter(
        and_(
            tables.Budget.user_id == 1,
            tables.Budget.month == month
        )
    ).all()
    
    results = []
    for budget in budgets:
        # Calcular gasto actual en la categoría
        spent = db.query(
            func.sum(tables.Expense.amount)
        ).filter(
            and_(
                tables.Expense.user_id == 1,
                tables.Expense.category_id == budget.category_id,
                extract('year', tables.Expense.date) == month.year,
                extract('month', tables.Expense.date) == month.month
            )
        ).scalar() or 0.0
        
        percentage = (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
        
        results.append({
            "budget_id": budget.id,
            "category_id": budget.category_id,
            "category_name": budget.category.name,
            "budget_limit": budget.amount_limit,
            "current_spent": spent,
            "remaining": budget.amount_limit - spent,
            "percentage_used": percentage,
            "alert_threshold": budget.alert_threshold * 100,
            "is_over_threshold": percentage >= (budget.alert_threshold * 100),
            "is_over_budget": spent > budget.amount_limit
        })
    
    return {
        "month": month,
        "budgets": results
    }


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas generales del usuario
    """
    user_id = 1  # TODO: Del token
    
    # Total de gastos
    total_expenses = db.query(
        func.count(tables.Expense.id)
    ).filter(
        tables.Expense.user_id == user_id
    ).scalar()
    
    # Suma total
    total_amount = db.query(
        func.sum(tables.Expense.amount)
    ).filter(
        tables.Expense.user_id == user_id
    ).scalar() or 0.0
    
    # Promedio por gasto
    avg_expense = db.query(
        func.avg(tables.Expense.amount)
    ).filter(
        tables.Expense.user_id == user_id
    ).scalar() or 0.0
    
    # Gasto más alto
    max_expense = db.query(
        func.max(tables.Expense.amount)
    ).filter(
        tables.Expense.user_id == user_id
    ).scalar() or 0.0
    
    # Categoría favorita
    favorite_category = db.query(
        tables.Category.name,
        func.count(tables.Expense.id).label('count')
    ).join(
        tables.Expense
    ).filter(
        tables.Expense.user_id == user_id
    ).group_by(
        tables.Category.id
    ).order_by(
        func.count(tables.Expense.id).desc()
    ).first()
    
    # Gastos este mes
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    this_month_total = db.query(
        func.sum(tables.Expense.amount)
    ).filter(
        and_(
            tables.Expense.user_id == user_id,
            tables.Expense.date >= month_start
        )
    ).scalar() or 0.0
    
    return {
        "total_expenses": total_expenses,
        "total_amount": float(total_amount),
        "average_expense": float(avg_expense),
        "max_expense": float(max_expense),
        "favorite_category": favorite_category.name if favorite_category else None,
        "this_month_total": float(this_month_total)
    }
