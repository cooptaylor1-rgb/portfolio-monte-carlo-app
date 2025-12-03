#!/bin/bash

# Setup script for Salem Portfolio Analysis
# Run this script to set up both backend and frontend

set -e

echo "🚀 Setting up Salem Portfolio Analysis..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Backend setup
echo "🔧 Setting up backend..."
cd backend

echo "  Creating virtual environment..."
python3 -m venv venv

echo "  Activating virtual environment..."
source venv/bin/activate

echo "  Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"
echo ""

cd ..

# Frontend setup
echo "🎨 Setting up frontend..."
cd frontend

echo "  Installing Node dependencies..."
npm install

echo "✅ Frontend setup complete"
echo ""

cd ..

# Create .env files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cat > backend/.env << EOF
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cat > frontend/.env << EOF
# Frontend Configuration
VITE_API_BASE_URL=/api
EOF
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "2. Start the frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to http://localhost:3000"
echo ""
echo "📚 View API docs at http://localhost:8000/api/docs"
echo ""
