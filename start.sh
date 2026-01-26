#!/bin/bash

# Script to start Expense AI Assistant

echo "🚀 Starting Expense AI Assistant..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source venv/bin/activate
fi

# Check if the database exists
if [ ! -f "data/database/expenses.db" ]; then
    echo -e "${YELLOW}⚠️  Database not found${NC}"
    echo "Would you like to initialize the database with sample data? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        python scripts/init_db.py
    else
        python -c "from backend.models.database import init_db; init_db()"
    fi
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${GREEN}    Expense AI Assistant - Starting...${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""

# Function to handle Ctrl+C (SIGINT)
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start the backend in the background
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
python backend/api/main.py &
BACKEND_PID=$!

# Wait for the backend to initialize
sleep 3

# Start the frontend
echo -e "${BLUE}🎨 Starting Frontend (Streamlit)...${NC}"
streamlit run frontend/streamlit/app.py &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Services started successfully!${NC}"
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo -e "   • Frontend: ${GREEN}http://localhost:8501${NC}"
echo -e "   • Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "   • API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop services${NC}"
echo ""

# Keep the script running to monitor background processes
wait
