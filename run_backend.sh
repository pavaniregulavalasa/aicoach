#!/bin/bash
# Backend startup script

cd /Users/raghukiran/Documents/personal/pavaniwork
source venv/bin/activate
uvicorn services.main:app --host 127.0.0.1 --port 8000 --reload

