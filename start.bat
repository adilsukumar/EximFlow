@echo off
cd /d "%~dp0"
title EximFlow AI Platform (Port 9090)
echo ====================================================
echo Starting EximFlow AI Platform (9000 Series)
echo Opening: http://localhost:9090
echo ====================================================
python run.py
pause
