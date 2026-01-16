from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = Field(default="Expense AI Assistant", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")
    
    # Database
    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR}/data/database/expenses.db",
        alias="DATABASE_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-please-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # OCR Settings
    ocr_engine: str = Field(default="easyocr", alias="OCR_ENGINE")
    ocr_languages: List[str] = Field(default=["en", "es"], alias="OCR_LANGUAGES")
    tesseract_path: str = Field(
        default="/usr/bin/tesseract",
        alias="TESSERACT_PATH"
    )
    
    # ML Models
    classifier_model_path: str = Field(
        default=str(BASE_DIR / "backend/ml/saved_models/classifier.pkl"),
        alias="CLASSIFIER_MODEL_PATH"
    )
    predictor_model_path: str = Field(
        default=str(BASE_DIR / "backend/ml/saved_models/predictor.pkl"),
        alias="PREDICTOR_MODEL_PATH"
    )
    min_confidence_threshold: float = Field(
        default=0.7,
        alias="MIN_CONFIDENCE_THRESHOLD"
    )
    
    # File Upload
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "pdf"],
        alias="ALLOWED_EXTENSIONS"
    )
    upload_dir: str = Field(
        default=str(BASE_DIR / "data/raw"),
        alias="UPLOAD_DIR"
    )
    
    # Frontend
    streamlit_server_port: int = Field(default=8501, alias="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(
        default="localhost",
        alias="STREAMLIT_SERVER_ADDRESS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(
        default=str(BASE_DIR / "logs/app.log"),
        alias="LOG_FILE"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Creates necessary directories for the application"""
        directories = [
            self.upload_dir,
            os.path.dirname(self.classifier_model_path),
            os.path.dirname(self.log_file),
            os.path.join(BASE_DIR, "data/database"),
            os.path.join(BASE_DIR, "data/processed"),
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
