"""Application constants"""

# Expense categories
EXPENSE_CATEGORIES = {
    "food": {
        "name": "Food & Dining",
        "subcategories": ["groceries", "restaurant", "cafe", "fast_food"],
        "color": "#4CAF50",
        "icon": "🍔",
        "keywords": ["walmart", "target", "whole foods", "kroger", "safeway", "restaurant", "bar", "cafe", "starbucks", "mcdonalds", "subway"]
    },
    "transportation": {
        "name": "Transportation",
        "subcategories": ["gas", "public_transport", "taxi", "parking"],
        "color": "#2196F3",
        "icon": "🚗",
        "keywords": ["gas", "shell", "chevron", "exxon", "bp", "metro", "bus", "train", "uber", "lyft", "parking"]
    },
    "housing": {
        "name": "Housing",
        "subcategories": ["rent", "mortgage", "utilities", "maintenance"],
        "color": "#FF9800",
        "icon": "🏠",
        "keywords": ["rent", "water", "electricity", "gas", "internet", "phone", "at&t", "verizon", "comcast"]
    },
    "health": {
        "name": "Health & Fitness",
        "subcategories": ["pharmacy", "doctor", "gym", "health_insurance"],
        "color": "#F44336",
        "icon": "⚕️",
        "keywords": ["pharmacy", "cvs", "walgreens", "doctor", "hospital", "clinic", "gym", "fitness", "planet fitness"]
    },
    "entertainment": {
        "name": "Entertainment",
        "subcategories": ["movies", "events", "hobbies", "travel"],
        "color": "#9C27B0",
        "icon": "🎮",
        "keywords": ["cinema", "theater", "concert", "spotify", "netflix", "hulu", "disney", "steam", "playstation", "xbox"]
    },
    "shopping": {
        "name": "Shopping",
        "subcategories": ["clothing", "electronics", "home", "other"],
        "color": "#E91E63",
        "icon": "🛍️",
        "keywords": ["amazon", "ebay", "best buy", "target", "macy", "nordstrom", "ikea", "home depot"]
    },
    "education": {
        "name": "Education",
        "subcategories": ["courses", "books", "supplies"],
        "color": "#00BCD4",
        "icon": "📚",
        "keywords": ["university", "college", "school", "course", "udemy", "coursera", "book", "amazon books"]
    },
    "other": {
        "name": "Other",
        "subcategories": [],
        "color": "#9E9E9E",
        "icon": "📦",
        "keywords": []
    }
}

# Payment methods
PAYMENT_METHODS = [
    "cash",
    "debit_card",
    "credit_card",
    "transfer",
    "paypal",
    "venmo",
    "other"
]

# Data sources
DATA_SOURCES = [
    "manual",      # Manually entered by user
    "ocr",         # Extracted from image via OCR
    "api",         # Imported from external API
    "csv_import"   # Imported from CSV
]

# OCR configuration
OCR_PATTERNS = {
    "total": [
        r"total[:\s]+([0-9]+[.,][0-9]{2})",
        r"amount[:\s]+([0-9]+[.,][0-9]{2})",
        r"\$\s*([0-9]+[.,][0-9]{2})",
        r"([0-9]+[.,][0-9]{2})\s*\$",
    ],
    "date": [
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{1,2}\s+\w+\s+\d{4})",
    ],
    "merchant": [
        r"^([A-Z\s]+)",  # First line in uppercase
    ]
}

# Analysis periods
ANALYSIS_PERIODS = {
    "week": "Last week",
    "month": "Last month",
    "quarter": "Last quarter",
    "year": "Last year",
    "all": "All history"
}

# Anomaly detection thresholds
ANOMALY_THRESHOLDS = {
    "z_score": 3.0,  # Standard deviations to consider anomaly
    "iqr_multiplier": 1.5  # Interquartile range multiplier
}

# Prediction configuration
PREDICTION_CONFIG = {
    "min_data_points": 30,  # Minimum records to make predictions
    "forecast_periods": 3,   # Number of periods to predict (months)
    "confidence_interval": 0.95
}

# Error messages
ERROR_MESSAGES = {
    "file_too_large": "File is too large. Maximum size: 10MB",
    "invalid_format": "Invalid file format. Use JPG, PNG or PDF",
    "ocr_failed": "Could not extract text from image",
    "no_amount_found": "Could not identify amount in receipt",
    "database_error": "Error saving to database",
    "model_not_found": "ML model not found",
    "insufficient_data": "Insufficient data to make predictions"
}

# Success messages
SUCCESS_MESSAGES = {
    "expense_created": "Expense recorded successfully",
    "expense_updated": "Expense updated successfully",
    "expense_deleted": "Expense deleted",
    "budget_set": "Budget configured",
    "data_imported": "Data imported successfully"
}

# Visualization configuration
CHART_COLORS = [
    "#4CAF50", "#2196F3", "#FF9800", "#F44336",
    "#9C27B0", "#E91E63", "#00BCD4", "#9E9E9E"
]

# Supported currencies
CURRENCIES = {
    "USD": {"symbol": "$", "name": "US Dollar"},
    "EUR": {"symbol": "€", "name": "Euro"},
    "GBP": {"symbol": "£", "name": "Pound Sterling"}
}

DEFAULT_CURRENCY = "USD"
