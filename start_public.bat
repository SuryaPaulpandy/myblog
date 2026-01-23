@echo off
echo ========================================
echo   Starting MyBlog for Public Access
echo ========================================
echo.
echo Step 1: Starting Django Server on port 8002...
start "Django Server" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python manage.py runserver 8002"
timeout /t 5 /nobreak >nul
echo.
echo Step 2: Please start ngrok manually:
echo   1. Open a new terminal
echo   2. Navigate to ngrok folder
echo   3. Run: ngrok http 8002
echo.
echo Your public URL will appear in ngrok!
echo Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
echo.
echo ========================================
pause
