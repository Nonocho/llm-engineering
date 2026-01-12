@echo off
REM Quick start script for CrewAI Data Scientists App
REM Run this to start the application

echo ============================================================
echo Starting CrewAI Data Scientists Application
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python app.py

REM Keep window open if there's an error
pause
