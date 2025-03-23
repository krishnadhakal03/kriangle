@echo off
echo Installing ReportLab for PDF generation...

REM Activate virtual environment
call venv\Scripts\activate

REM Install ReportLab package
pip install reportlab==4.0.5

echo.
echo Installation complete! ReportLab should now be available.
echo You can now restart your Django server.
echo.
pause 