from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import numpy as np
import logging

from backend.models import tables
from backend.config.constants import ANOMALY_THRESHOLDS

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for expense data analysis"""
    
    def get_period_summary(
        self,
        db: Session,
        user_id: int,
        period: str,
        category_id: Optional[int] = None
    ) -> Dict:
        """
        Retrieves a summary for a specific time period
        """
        # Calculate dates
        end_date = datetime.now()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "quarter":
            start_date = end_date - timedelta(days=90)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:  # all time
            start_date = datetime(2000, 1, 1)
        
        # Base Query
        query = db.query(
            func.sum(tables.Expense.amount).label("total"),
            func.count(tables.Expense.id).label("count"),
            func.avg(tables.Expense.amount).label("average")
        ).filter(
            and_(
                tables.Expense.user_id == user_id,
                tables.Expense.date >= start_date,
                tables.Expense.date <= end_date
            )
        )
        
        if category_id:
            query = query.filter(tables.Expense.category_id == category_id)
        
        result = query.first()
        
        # Calculate daily average
        days = (end_date - start_date).days or 1
        avg_per_day = (result.total or 0) / days
        
        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_expenses": float(result.total or 0),
            "total_transactions": result.count,
            "average_per_transaction": float(result.average or 0),
            "average_per_day": avg_per_day
        }
    
    def get_trends(
        self,
        db: Session,
        user_id: int,
        period: str,
        group_by: str,
        category_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieves grouped spending trends
        """
        # Calculate dates
        end_date = datetime.now()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Build query based on grouping
        if group_by == "day":
            query = db.query(
                func.date(tables.Expense.date).label('date'),
                func.sum(tables.Expense.amount).label('total'),
                func.count(tables.Expense.id).label('count')
            )
        elif group_by == "week":
            query = db.query(
                extract('year', tables.Expense.date).label('year'),
                extract('week', tables.Expense.date).label('week'),
                func.sum(tables.Expense.amount).label('total'),
                func.count(tables.Expense.id).label('count')
            )
        else:  # month
            query = db.query(
                extract('year', tables.Expense.date).label('year'),
                extract('month', tables.Expense.date).label('month'),
                func.sum(tables.Expense.amount).label('total'),
                func.count(tables.Expense.id).label('count')
            )
        
        query = query.filter(
            and_(
                tables.Expense.user_id == user_id,
                tables.Expense.date >= start_date,
                tables.Expense.date <= end_date
            )
        )
        
        if category_id:
            query = query.filter(tables.Expense.category_id == category_id)
        
        if group_by == "day":
            query = query.group_by(func.date(tables.Expense.date))
            query = query.order_by(func.date(tables.Expense.date))
        else:
            query = query.group_by('year', group_by)
            query = query.order_by('year', group_by)
        
        results = query.all()
        
        # Format results
        trends = []
        for row in results:
            if group_by == "day":
                trends.append({
                    "date": row.date.isoformat(),
                    "total": float(row.total),
                    "count": row.count
                })
            else:
                trends.append({
                    "year": int(row.year),
                    group_by: int(getattr(row, group_by)),
                    "total": float(row.total),
                    "count": row.count
                })
        
        return trends
    
    def detect_anomalies(
        self,
        db: Session,
        user_id: int,
        threshold: float = None
    ) -> List[Dict]:
        """
        Detects anomalous expenses using Z-score logic
        """
        if threshold is None:
            threshold = ANOMALY_THRESHOLDS["z_score"]
        
        # Get all expenses
        expenses = db.query(tables.Expense).filter(
            tables.Expense.user_id == user_id
        ).all()
        
        if len(expenses) < 10:
            return []  # Insufficient data for reliable detection
        
        # Extract amounts
        amounts = [e.amount for e in expenses]
        
        # Calculate statistics
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        if std == 0:
            return []
        
        # Detect anomalies
        anomalies = []
        for expense in expenses:
            z_score = abs((expense.amount - mean) / std)
            
            if z_score > threshold:
                anomalies.append({
                    "expense_id": expense.id,
                    "date": expense.date,
                    "merchant": expense.merchant,
                    "amount": expense.amount,
                    "category": expense.category.name,
                    "z_score": float(z_score),
                    "deviation": expense.amount - mean
                })
        
        # Sort by z_score descending
        anomalies.sort(key=lambda x: x["z_score"], reverse=True)
        
        return anomalies[:20]  # Return top 20 anomalies
    
    def calculate_category_insights(
        self,
        db: Session,
        user_id: int,
        period_days: int = 30
    ) -> List[Dict]:
        """
        Calculates spending insights per category
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        query = db.query(
            tables.Category.id,
            tables.Category.name,
            tables.Category.icon,
            func.sum(tables.Expense.amount).label("total"),
            func.count(tables.Expense.id).label("count"),
            func.avg(tables.Expense.amount).label("average"),
            func.max(tables.Expense.amount).label("max_expense")
        ).join(
            tables.Expense
        ).filter(
            and_(
                tables.Expense.user_id == user_id,
                tables.Expense.date >= start_date,
                tables.Expense.date <= end_date
            )
        ).group_by(
            tables.Category.id
        ).order_by(
            func.sum(tables.Expense.amount).desc()
        ).all()
        
        total_spending = sum([r.total for r in query])
        
        insights = []
        for row in query:
            percentage = (row.total / total_spending * 100) if total_spending > 0 else 0
            
            insights.append({
                "category_id": row.id,
                "category_name": row.name,
                "icon": row.icon,
                "total": float(row.total),
                "count": row.count,
                "average": float(row.average),
                "max_expense": float(row.max_expense),
                "percentage": percentage,
                "trend": self._calculate_trend(db, user_id, row.id, period_days)
            })
        
        return insights
    
    def _calculate_trend(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        period_days: int
    ) -> str:
        """
        Calculates if the spending trend is increasing, decreasing, or stable
        """
        end_date = datetime.now()
        mid_date = end_date - timedelta(days=period_days // 2)
        start_date = end_date - timedelta(days=period_days)
        
        # First half of the period
        first_half = db.query(
            func.sum(tables.Expense.amount)
        ).filter(
            and_(
                tables.Expense.user_id == user_id,
                tables.Expense.category_id == category_id,
                tables.Expense.date >= start_date,
                tables.Expense.date < mid_date
            )
        ).scalar() or 0
        
        # Second half of the period
        second_half = db.query(
            func.sum(tables.Expense.amount)
        ).filter(
            and_(
                tables.Expense.user_id == user_id,
                tables.Expense.category_id == category_id,
                tables.Expense.date >= mid_date,
                tables.Expense.date <= end_date
            )
        ).scalar() or 0
        
        if first_half == 0:
            return "new"
        
        change = ((second_half - first_half) / first_half) * 100
        
        if change > 10:
            return "up"
        elif change < -10:
            return "down"
        else:
            return "stable"


# Global instance
analytics_service = AnalyticsService()
