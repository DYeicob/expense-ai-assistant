# 🚀 Quick Start Guide - Expense AI Assistant

This guide will help you get the project up and running in **less than 5 minutes**.

## ⚡ Quick Start (Easiest Method)

### On Linux/Mac:

```bash
# 1. Clone and enter directory
cd expense-ai-assistant

# 2. Give execution permissions to script
chmod +x start.sh

# 3. Run
./start.sh
```

### On Windows:

```bash
# 1. Navigate to directory
cd expense-ai-assistant

# 2. Run script
start.bat
```

That's it! The script will handle:
- Creating virtual environment if it doesn't exist
- Installing all dependencies
- Initializing the database
- Starting both backend and frontend

## 🔧 Manual Installation (Step by Step)

### Step 1: Prerequisites

Make sure you have installed:
- Python 3.9 or higher
- pip
- git

```bash
python --version  # Should be 3.9+
pip --version
```

### Step 2: Clone Repository

```bash
git clone <your-repository>
cd expense-ai-assistant
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: Installation may take several minutes, especially EasyOCR which is heavy.

### Step 5: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your preferences (optional)
nano .env  # or use your favorite editor
```

### Step 6: Initialize Database

You have two options:

**Option A: With sample data (recommended for testing)**
```bash
python scripts/init_db.py
```

**Option B: Empty database**
```bash
python -c "from backend.models.database import init_db; init_db()"
```

### Step 7: Start Application

**Terminal 1 - Backend (API):**
```bash
python backend/api/main.py
```

**Terminal 2 - Frontend (Streamlit):**
```bash
streamlit run frontend/streamlit/app.py
```

## 🌐 Access Application

Once started, open your browser at:

- **Frontend (UI)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📝 First Steps

### 1. Explore Dashboard
- Navigate to http://localhost:8501
- You'll see the main dashboard with metrics

### 2. Add Your First Expense
- Go to "➕ Add Expense"
- Fill out the form
- Click "Save"

### 3. Test OCR
- Go to "📤 Upload Receipt"
- Upload a receipt photo
- AI will automatically extract:
  - Date
  - Merchant
  - Total amount
  - Suggested category

### 4. View Analytics
- Go to "📈 Analytics"
- Explore charts and statistics
- Filter by period and category

## 🐳 With Docker (Alternative)

If you prefer using Docker:

```bash
# Build and start
cd docker
docker-compose up --build

# Application will be available at:
# - Frontend: http://localhost:8501
# - Backend: http://localhost:8000
```

## ❓ Common Issues

### Error: "No module named 'backend'"

**Solution**: Make sure you're in the project root directory.

```bash
cd expense-ai-assistant
python backend/api/main.py
```

### Error: "Database not found"

**Solution**: Initialize the database:

```bash
python scripts/init_db.py
```

### Error installing EasyOCR (Windows)

**Solution**: Install Visual C++ Build Tools:
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install and restart
- Run `pip install -r requirements.txt` again

### Port 8000 or 8501 already in use

**Solution**: Change ports in `.env`:

```env
API_PORT=8001
STREAMLIT_SERVER_PORT=8502
```

### Permission error on Linux/Mac

**Solution**: Give permissions to script:

```bash
chmod +x start.sh
```

## 🎯 Next Steps

1. **Customize Categories**: Edit `backend/config/constants.py`
2. **Train Classifier**: Add more expenses to improve accuracy
3. **Configure Budgets**: Set monthly limits by category
4. **Explore API**: Go to http://localhost:8000/docs

## 📚 Additional Documentation

- [Complete README](README.md) - Full project documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture](README.md#project-structure) - Project structure

## 💡 Tips

- **Data backup**: SQLite database is in `data/database/expenses.db`
- **Logs**: Logs are saved in `logs/app.log`
- **Images**: Receipt photos are saved in `data/raw/`
- **ML Models**: Trained models are in `backend/ml/saved_models/`

## 🆘 Support

If you have issues:

1. Check [Common Issues](#common-issues) section
2. Check logs in `logs/app.log`
3. Open an issue on GitHub
4. Contact development team

---

Enjoy using Expense AI Assistant! 💰✨
