# 🚀 Quick Start Commands

## Prerequisites

1. **Activate Virtual Environment** (if not already activated):
   ```bash
   source venv/bin/activate
   ```

2. **Configure `.env` file** (if not already done):
   ```bash
   # For local Ollama
   LLM_MODE=local
   LLM_MODEL=qwen2.5-7b
   
   # OR for remote ELI gateway
   LLM_MODE=remote
   LLM_API_KEY=your-api-key
   LLM_BASE_URL=https://your-gateway-url/v1
   ```

## Running the Services

### Option 1: Using Shell Scripts (Easiest)

**Terminal 1 - Backend:**
```bash
./run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
uvicorn services.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
source venv/bin/activate
streamlit run app.py --server.port 8501
```

### Option 3: Windows Commands

**Terminal 1 - Backend:**
```cmd
venv\Scripts\activate
uvicorn services.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```cmd
venv\Scripts\activate
streamlit run app.py --server.port 8501
```

## Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## Troubleshooting

### Port Already in Use

If port 8000 or 8501 is already in use:

**Backend (different port):**
```bash
uvicorn services.main:app --host 127.0.0.1 --port 8001 --reload
```

**Frontend (different port):**
```bash
streamlit run app.py --server.port 8502
```

### Virtual Environment Not Found

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Backend Not Starting

1. Check if `.env` file exists
2. Verify virtual environment is activated
3. Check logs in `logs/` directory
4. Ensure all dependencies are installed

### Frontend Can't Connect to Backend

1. Verify backend is running on port 8000
2. Check `app.py` - it should connect to `http://127.0.0.1:8000`
3. Test backend health: `curl http://127.0.0.1:8000/health`

