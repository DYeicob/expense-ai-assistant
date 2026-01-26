from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums
class PaymentMethod(str, Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    TRANSFER = "transfer"
    PAYPAL = "paypal"
    VENMO = "venmo"
    OTHER = "other"


class DataSource(str, Enum):
    MANUAL = "manual"
    OCR = "ocr"
    API = "api"
    CSV_IMPORT = "csv_import"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_category_id: Optional[int] = None
    color: str = "#9E9E9E"
    icon: str = "📦"
    keywords: List[str] = []


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    keywords: Optional[List[str]] = None


class CategoryInDB(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Expense schemas
class ExpenseBase(BaseModel):
    date: datetime
    merchant: Optional[str] = None
    category_id: int
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    is_recurring: bool = False


class ExpenseCreate(ExpenseBase):
    user_id: Optional[int] = None  # Automatically assigned from token
    source: DataSource = DataSource.MANUAL


class ExpenseUpdate(BaseModel):
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    is_recurring: Optional[bool] = None


class ExpenseInDB(ExpenseBase):
    id: int
    user_id: int
    source: str
    image_path: Optional[str]
    confidence: Optional[float]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Nested data
    category: Optional[CategoryInDB] = None
    
    class Config:
        from_attributes = True


# Budget schemas
class BudgetBase(BaseModel):
    category_id: int
    month: datetime
    amount_limit: float = Field(..., gt=0)
    alert_threshold: float = Field(default=0.8, ge=0, le=1)


class BudgetCreate(BudgetBase):
    user_id: Optional[int] = None


class BudgetUpdate(BaseModel):
    amount_limit: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[float] = Field(None, ge=0, le=1)


class BudgetInDB(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Calculated data
    current_spent: Optional[float] = None
    percentage_used: Optional[float] = None
    
    category: Optional[CategoryInDB] = None
    
    class Config:
        from_attributes = True


# Prediction schemas
class PredictionBase(BaseModel):
    category_id: int
    month: datetime
    predicted_amount: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: Optional[float] = None


class PredictionInDB(PredictionBase):
    id: int
    user_id: int
    model_version: Optional[str]
    created_at: datetime
    
    category: Optional[CategoryInDB] = None
    
    class Config:
        from_attributes = True


# OCR schemas
class OCRResult(BaseModel):
    text: str
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    confidence: float
    raw_data: Dict[str, Any] = {}


class UploadReceiptResponse(BaseModel):
    success: bool
    message: str
    ocr_result: Optional[OCRResult] = None
    expense_id: Optional[int] = None


# Analytics schemas
class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    average_amount: float
    percentage: float


class PeriodSummary(BaseModel):
    period: str
    total_expenses: float
    total_transactions: int
    average_per_day: float
    by_category: List[CategorySummary]


class TrendData(BaseModel):
    date: datetime
    amount: float
    category: Optional[str] = None


class AnalyticsResponse(BaseModel):
    summary: PeriodSummary
    trends: List[TrendData]
    top_merchants: List[Dict[str, Any]]
    anomalies: List[ExpenseInDB] = []


# Generic response schemas
class MessageResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
