# AI Coach - Telecom Training Platform

AI-powered training platform for telecom systems using LangChain, FastAPI, and Streamlit.

## Requirements

- Python 3.13+
- See `requirements.txt` for all dependencies

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```bash
# For local Ollama
LLM_MODE=local
LLM_MODEL=qwen2.5:7b

# OR for remote ELI gateway
LLM_MODE=remote
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-gateway-url/v1
```

### 3. Run Services

**Terminal 1 - Backend:**
```bash
./run_backend.sh
# OR
uvicorn services.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
# OR
streamlit run app.py --server.port 8501
```

### 4. Access Application
- Frontend: http://localhost:8501
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

## Documentation

- `LAUNCH_GUIDE.md` - Detailed setup instructions
- `QUICK_START.md` - Quick reference commands
- `OLLAMA_SETUP.md` - Local Ollama setup guide
- `RUN_COMMANDS.md` - All run commands reference
