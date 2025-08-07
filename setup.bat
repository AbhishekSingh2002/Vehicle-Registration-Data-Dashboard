@echo off
REM Script to set up the development environment for Vehicle Registration Dashboard

echo Setting up Python virtual environment...
python -m venv venv

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment. Please ensure Python 3.8+ is installed and in PATH.
    pause
    exit /b %ERRORLEVEL%
)

call venv\Scripts\activate

if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %ERRORLEVEL%
)

echo Upgrading pip...
python -m pip install --upgrade pip

if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip.
    pause
    exit /b %ERRORLEVEL%
)

echo Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Setup completed successfully!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo To run the dashboard, use:
echo   streamlit run app.py
echo.
pause
