@echo off
REM Quick Start Script for Windows
REM Carpool RideShare Application

echo.
echo  RideShare - Carpool Pricing Application
echo  =========================================
echo.

echo Checking Python installation...
python --version

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Launching Streamlit app...
echo.
echo App running at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the app
echo.

streamlit run carpool_streamlit_app.py

pause
