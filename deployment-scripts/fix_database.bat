@echo off
echo Database Fix Script - Kriangle
echo =============================

REM Activate virtual environment
call venv\Scripts\activate

REM Run the database fix script
python fix_database.py

echo.
echo If you see any errors above, please contact support.
echo.
pause 