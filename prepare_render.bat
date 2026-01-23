@echo off
echo ========================================
echo   Preparing for Render Deployment
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Running migrations (creates db.sqlite3)...
python manage.py migrate

echo.
echo Step 3: Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Step 4: Checking files...
if exist db.sqlite3 (
    echo [OK] db.sqlite3 exists
) else (
    echo [ERROR] db.sqlite3 not found!
)

if exist staticfiles (
    echo [OK] staticfiles folder exists
) else (
    echo [ERROR] staticfiles folder not found!
)

echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Check that db.sqlite3 and staticfiles/ are ready
echo 2. Run: git add .
echo 3. Run: git commit -m "Prepare for Render deployment"
echo 4. Run: git push origin main
echo 5. Go to Render dashboard and deploy
echo.
echo ========================================
pause
