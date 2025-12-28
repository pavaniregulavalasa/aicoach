# 🚀 Launch Guide

## 📋 Prerequisites

### System Requirements
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning)

---

## 🔧 Initial Setup

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd /Users/raghukiran/Documents/personal/pavaniwork

# Create virtual environment
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

**Expected output**: Your terminal prompt should show `(venv)` prefix.

### Step 2: Install Dependencies

```bash
# Ensure virtual environment is activated (you should see (venv) in prompt)
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Installation time**: ~2-5 minutes depending on internet speed.

**What gets installed**:
- FastAPI & Uvicorn (backend server)
- Streamlit (frontend framework)
- LangChain & AI libraries
- FAISS (vector database)
- PDF processing libraries
- And more...

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your credentials
# Use your preferred editor:
nano .env
# or
code .env
# or
vim .env
```

**Required variables in `.env`**:
```bash
ELI_API_KEY=your-eli-api-key-here
ELI_BASE_URL=https://gateway.eli.gaia.gic.ericsson.se/api/openai/v1
```

**Security Note**: Never commit `.env` file to git! It's already in `.gitignore`.

### Step 4: Create FAISS Indexes (Optional but Recommended)

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Place your PDF documents in:
# - knowledge/mml/ (for MML training)
# - knowledge/alarm_handling/ (for alarm handling training)

# Run the RAG indexing script
python services/rag.py
```

**Expected output**: 
```
📁 Found 2 subfolders: ['mml', 'alarm_handling']
🔄 Processing: mml
📄 Loaded X PDFs
✅ mml: X chunks → services/faiss_indexes/mml/
...
🎉 All FAISS indexes created!
```

---

## 🚀 Running the Application

### Option 1: Run Both Services (Recommended)

**Terminal 1 - Backend:**
```bash
cd /Users/raghukiran/Documents/personal/pavaniwork
source venv/bin/activate
uvicorn services.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd /Users/raghukiran/Documents/personal/pavaniwork
source venv/bin/activate
streamlit run app.py --server.port 8501
```

**Note**: `app.py` is in the root directory. If you see errors, ensure you're running from the project root.

### Option 2: Use Provided Scripts

**Backend:**
```bash
./run_backend.sh
```

**Frontend:**
```bash
# Create run_frontend.sh or run manually:
source venv/bin/activate
streamlit run app.py --server.port 8501
```

---

## 🌐 Access Points

### Frontend (Streamlit)
- **URL**: http://localhost:8501
- **Main Page**: Landing page with navigation
- **Pages**:
  - Training Agent (`pages/1_training.py`)
  - Mentor Agent (`pages/2_mentor.py`)
  - Assessment (`pages/3_assessment.py`)

### Backend (FastAPI)
- **API URL**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs (Interactive Swagger UI)
- **Health Check**: http://127.0.0.1:8000/health

### API Endpoints:
- `GET /health` - Health check endpoint
- `POST /training` - Generate training content
- `POST /mentor` - Get mentor guidance
- `POST /assessment` - Evaluate user approach

---

## 🔍 Verification

### Check Backend:
```bash
curl http://127.0.0.1:8000/health
```

**Expected response**:
```json
{"status":"healthy","service":"AI Telecom Training Coach API"}
```

### Check Frontend:
Open browser to http://localhost:8501 - you should see the AI Coach landing page.

---

## 🛠️ Troubleshooting

### Virtual Environment Issues

**Problem**: `venv/bin/activate: No such file or directory`
```bash
# Solution: Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

**Problem**: `pip: command not found`
```bash
# Solution: Install pip or use python3 -m pip
python3 -m pip install -r requirements.txt
```

### Dependency Installation Issues

**Problem**: `ERROR: Could not find a version that satisfies the requirement`
```bash
# Solution: Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

**Problem**: SSL/Certificate errors during installation
```bash
# Solution: Use trusted hosts or check network/VPN
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: `Address already in use` (port 8000)
```bash
# Solution: Use a different port
uvicorn services.main:app --host 127.0.0.1 --port 8001 --reload
# Then update frontend to use port 8001
```

### Frontend Issues

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`
```bash
# Solution: Install dependencies
source venv/bin/activate
pip install streamlit
```

**Problem**: Port 8501 already in use
```bash
# Solution: Use a different port
streamlit run app.py --server.port 8502
```

### FAISS Index Issues

**Problem**: `FileNotFoundError: No knowledge bases found`
```bash
# Solution: Create FAISS indexes
python services/rag.py
```

**Problem**: `pymupdf package not found`
```bash
# Solution: Install pymupdf
pip install pymupdf
```

### Environment Variable Issues

**Problem**: `ELI_API_KEY not found in environment variables`
```bash
# Solution: Create .env file
cp .env.example .env
# Edit .env and add your API key
```

---

## 📝 Quick Reference

### Activate Virtual Environment
```bash
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Check Installed Packages
```bash
pip list
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Check Python Version
```bash
python3 --version  # Should be 3.8+
```

---

## 🎯 Next Steps After Setup

1. ✅ Virtual environment created and activated
2. ✅ Dependencies installed
3. ✅ Environment variables configured (`.env` file)
4. ✅ FAISS indexes created (if you have PDFs)
5. ✅ Backend running on port 8000
6. ✅ Frontend running on port 8501

**You're ready to use the AI Telecom Training Coach!** 🎉

---

## 📚 Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs
- **Environment Setup**: See `.env.example` for required variables
- **Project Structure**: See `ARCHITECTURE_ANALYSIS.md` (if available)

---

## Troubleshooting

### Frontend can't connect to backend:
- Ensure backend is running on port 8000
- Check `http://127.0.0.1:8000/health` responds

### Missing dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Port already in use:
- Backend: Change port in uvicorn command
- Frontend: Use `--server.port 8502` or different port

