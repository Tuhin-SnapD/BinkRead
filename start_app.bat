@echo off
echo Starting BinkRead Application...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set environment variables for development
set FLASK_ENV=development
set SECRET_KEY=dev-secret-key-for-binkread
set FLASK_DEBUG=True

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    echo Creating uploads directory...
    mkdir uploads
)

echo.
echo Starting BinkRead application...
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

REM Start the Flask application
python app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application stopped with an error.
    pause
)

