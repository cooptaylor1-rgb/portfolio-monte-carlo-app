# Quick Start Guide

## Fastest Way to Get Started

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

Then follow the on-screen instructions to start both servers.

### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/docs
- API Health: http://localhost:8000/api/health

## First Steps After Setup

1. **Check API Health**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **List Available Presets**:
   ```bash
   curl http://localhost:8000/api/presets/
   ```

3. **Run a Test Simulation**:
   ```bash
   curl -X POST http://localhost:8000/api/simulation/run \
     -H "Content-Type: application/json" \
     -d @test_request.json
   ```

4. **Open Frontend**: Navigate to http://localhost:3000

## Testing the API

Run backend tests:
```bash
cd backend
pytest tests/ -v
```

## Common Issues

### Port Already in Use
- Backend (8000): Change in `backend/main.py`
- Frontend (3000): Change in `frontend/vite.config.ts`

### Module Not Found Errors
- Backend: Activate venv first: `source venv/bin/activate`
- Frontend: Run `npm install` in frontend directory

### CORS Errors
- Ensure backend is running on port 8000
- Check `frontend/vite.config.ts` proxy configuration

## Next Steps

1. Explore API documentation at http://localhost:8000/api/docs
2. Review `MIGRATION_README.md` for architecture details
3. Check `frontend/src/types/index.ts` for TypeScript types
4. Read `backend/models/schemas.py` for API contracts

## Quick Reference

### Backend Commands
```bash
# Start server
python main.py

# Run tests
pytest tests/ -v

# Check types
mypy backend/
```

### Frontend Commands
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Support

For issues or questions:
1. Check API logs in terminal
2. Check browser console for frontend errors
3. Review API docs at http://localhost:8000/api/docs
4. See detailed README at `MIGRATION_README.md`
