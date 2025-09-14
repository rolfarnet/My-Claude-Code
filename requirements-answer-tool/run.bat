@echo off
echo Starting Requirements Answer Tool...
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your ANTHROPIC_API_KEY
    echo Then run this script again.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
uv sync

REM Start the application
echo Starting the application...
echo Access the web interface at: http://localhost:8001/app
echo API documentation at: http://localhost:8001/docs
echo.
cd backend && uv run uvicorn app:app --reload --port 8001