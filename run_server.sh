#!/bin/bash

# FGI Backend Server 실행 스크립트

echo "🚀 Starting FGI Backend Server..."
echo "================================================"
echo ""
echo "Server will be available at: http://localhost:8000"
echo "API endpoint: http://localhost:8000/api/fgi/stream"
echo ""
echo "To stop the server, press Ctrl+C"
echo "================================================"
echo ""

# 가상환경 활성화 및 서버 실행
source .venv/bin/activate
python server.py
