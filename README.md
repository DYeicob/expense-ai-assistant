# 💰 Expense AI Assistant

Intelligent personal expense management system with AI for automatic receipt data extraction and predictive analysis.

## 🚀 Features

### ✅ Implemented (MVP)
- **Receipt OCR**: Automatic data extraction from receipt photos using EasyOCR
- **Smart Classification**: Automatic expense categorization using Machine Learning
- **REST API**: Complete backend with FastAPI
- **Interactive Dashboard**: Expense visualization with Streamlit
- **Expense Management**: Complete CRUD for personal expenses
- **Basic Analytics**: Summaries by period and category

### 🚧 In Development
- **Predictions**: Future expense forecasting with Prophet/LSTM
- **Anomaly Detection**: Identification of unusual expenses
- **Budgets**: Alert and limit system by category
- **Authentication**: User system with JWT
- **Export**: Reports in PDF and CSV

## 📋 Requirements

- Python 3.9+
- pip
- Tesseract OCR (optional, if using Tesseract instead of EasyOCR)

## 🛠️ Installation

### 1. Clone repository

```bash
git clone <your-repo>
cd expense-ai-assistant
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Initialize database

```bash
python -c "from backend.models.database import init_db; init_db()"
```

## 🚀 Usage

### Start Backend (API)

```bash
# From root directory
python backend/api/main.py

# Or using uvicorn directly
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
- Interactive documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

### Start Frontend (Streamlit)

```bash
# In another terminal
streamlit run frontend/streamlit/app.py
```

Frontend will be available at: `http://localhost:8501`

## 📁 Project Structure

```
expense-ai-assistant/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   │   ├── expenses.py      # CRUD de gastos
│   │   │   ├── upload.py        # Upload de tickets
│   │   │   ├── analytics.py     # Estadísticas e insights
│   │   │   └── predictions.py   # Predicciones
│   │   └── dependencies.py      # Dependencias compartidas
│   │
│   ├── services/
│   │   ├── ocr_service.py       # Extracción de texto
│   │   ├── parser_service.py    # Parseo de datos del ticket
│   │   ├── classifier_service.py # Clasificación de categorías
│   │   ├── prediction_service.py # Predicciones
│   │   └── analytics_service.py  # Análisis y agregaciones
│   │
│   ├── models/
│   │   ├── database.py          # Configuración DB
│   │   ├── schemas.py           # Pydantic schemas (DTOs)
│   │   └── tables.py            # SQLAlchemy models
│   │
│   ├── ml/
│   │   ├── classifier/
│   │   │   ├── train.py         # Entrenamiento del clasificador
│   │   │   ├── model.py         # Definición del modelo
│   │   │   └── data/            # Datasets de entrenamiento
│   │   ├── predictor/
│   │   │   ├── train.py         # Modelo de predicción
│   │   │   └── model.py
│   │   └── saved_models/        # Modelos entrenados (.pkl, .h5)
│   │
│   ├── utils/
│   │   ├── image_processing.py  # Preprocesamiento de imágenes
│   │   ├── text_processing.py   # Limpieza de texto
│   │   └── validators.py        # Validaciones
│   │
│   └── config/
│       ├── settings.py          # Configuraciones (env vars)
│       └── constants.py         # Constantes (categorías, etc.)
│
├── frontend/
│   ├── streamlit/               # Si usas Streamlit
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── 1_upload.py
│   │   │   ├── 2_dashboard.py
│   │   │   ├── 3_analytics.py
│   │   │   └── 4_predictions.py
│   │   └── components/
│   │       ├── charts.py
│   │       └── forms.py
│   │
│   └── react/                   # Alternativa con React
│       ├── src/
│       ├── public/
│       └── package.json
│
├── data/
│   ├── raw/                     # Imágenes originales
│   ├── processed/               # Datos procesados
│   └── database/                # SQLite file
│
├── tests/
│   ├── test_ocr.py
│   ├── test_classifier.py
│   └── test_api.py
│
├── notebooks/                   # Jupyter notebooks para exploración
│   ├── 01_ocr_exploration.ipynb
│   ├── 02_classifier_training.ipynb
│   └── 03_data_analysis.ipynb
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── setup.py
```

## 🔧 Configuration

### Main Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./data/database/expenses.db

# OCR
OCR_ENGINE=easyocr
OCR_LANGUAGES=["en", "es"]

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 API Usage

### Create an expense

```bash
curl -X POST "http://localhost:8000/api/expenses/" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15T10:00:00",
    "merchant": "Walmart",
    "category_id": 1,
    "amount": 45.50,
    "description": "Weekly shopping"
  }'
```

### Upload a receipt

```bash
curl -X POST "http://localhost:8000/api/upload/receipt" \
  -F "file=@/path/to/receipt.jpg" \
  -F "auto_save=true"
```

### Get analytics

```bash
curl "http://localhost:8000/api/analytics/summary?period=month"
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend tests/

# Specific tests
pytest tests/test_ocr.py
```

## 🎯 Roadmap

### Phase 1: MVP (✅ Completed)
- [x] Project structure
- [x] Database and models
- [x] Basic REST API
- [x] Receipt OCR
- [x] Expense classifier
- [x] Basic frontend with Streamlit
- [x] Basic analytics

### Phase 2: AI Improvements (🚧 In progress)
- [ ] Future expense predictions
- [ ] Anomaly detection
- [ ] Budget recommendations
- [ ] Classifier improvement with real data

### Phase 3: Advanced Features
- [ ] Authentication system
- [ ] Multi-user
- [ ] Bank import (API)
- [ ] Mobile app
- [ ] Notifications and alerts
- [ ] Report export

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is under the MIT License.

## 👤 Author

Jacobo Montero Naranjo.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR
- [Streamlit](https://streamlit.io/) - Frontend
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [scikit-learn](https://scikit-learn.org/) - Machine Learning

## 📞 Support

If you have questions or issues:
- Open an [Issue](https://github.com/DYeicob/expense-ai-assistant/issues)
- Contact via email: monteronaranjacobo@gmail.com

---

⭐ If you find this project useful, consider giving it a star!
