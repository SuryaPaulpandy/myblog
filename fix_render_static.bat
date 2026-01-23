@echo off
echo ========================================
echo   Fixing Static Files for Render
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Removing old staticfiles folder...
if exist staticfiles rmdir /s /q staticfiles

echo.
echo Step 3: Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Step 4: Checking staticfiles folder...
if exist staticfiles (
    echo [OK] staticfiles folder created
    dir staticfiles /b | find /c /v "" > temp_count.txt
    set /p file_count=<temp_count.txt
    del temp_count.txt
    echo [OK] Found %file_count% items in staticfiles
) else (
    echo [ERROR] staticfiles folder not created!
    pause
    exit /b 1
)

echo.
echo Step 5: Checking .gitignore...
findstr /C:"staticfiles" .gitignore >nul
if %errorlevel% equ 0 (
    echo [WARNING] staticfiles is in .gitignore - you may need to remove it
) else (
    echo [OK] staticfiles is NOT ignored
)

echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Check staticfiles/ folder exists
echo 2. Run: git add staticfiles/
echo 3. Run: git commit -m "Fix static files"
echo 4. Run: git push origin main
echo 5. Redeploy on Render
echo.
echo ========================================
pause
