@echo off
REM Screenshot Helper for ISP Management System
REM This script will help you take screenshots of all pages

echo ========================================
echo   ISP Management System Screenshots
echo ========================================
echo.
echo This script will help you take screenshots of all pages.
echo Make sure your Django server is running first!
echo.
echo Starting screenshot process...
echo.

REM Check if Django server is running
echo Checking if Django server is accessible...
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Django server is not running!
    echo Please start your server with: python manage.py runserver
    echo.
    pause
    exit /b 1
)

echo Django server is running! Starting screenshot process...
echo.

REM Create a list of URLs to screenshot
echo Opening pages for screenshots...
echo.

REM Authentication pages
echo 1. Opening Login page...
start http://127.0.0.1:8000/login
timeout /t 3 /nobreak >nul

echo 2. Opening Dashboard...
start http://127.0.0.1:8000/
timeout /t 3 /nobreak >nul

echo 3. Opening Users page...
start http://127.0.0.1:8000/users/
timeout /t 3 /nobreak >nul

echo 4. Opening Create User page...
start http://127.0.0.1:8000/createuser/
timeout /t 3 /nobreak >nul

echo 5. Opening Plans page...
start http://127.0.0.1:8000/plans/
timeout /t 3 /nobreak >nul

echo 6. Opening Create Plan page...
start http://127.0.0.1:8000/createplan/
timeout /t 3 /nobreak >nul

echo 7. Opening Billing page...
start http://127.0.0.1:8000/bill/
timeout /t 3 /nobreak >nul

echo 8. Opening Reports page...
start http://127.0.0.1:8000/reports/
timeout /t 3 /nobreak >nul

echo 9. Opening Analytics page...
start http://127.0.0.1:8000/analytics/
timeout /t 3 /nobreak >nul

echo 10. Opening Email page...
start http://127.0.0.1:8000/email/
timeout /t 3 /nobreak >nul

echo 11. Opening Admin panel...
start http://127.0.0.1:8000/admin/
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo All pages have been opened!
echo ========================================
echo.
echo Now take screenshots of each page:
echo.
echo 1. Use Win+Shift+S for Windows Snipping Tool
echo 2. Or use browser Developer Tools (F12) > Screenshot
echo 3. Save screenshots in appropriate folders:
echo    - screenshots\authentication\ for login pages
echo    - screenshots\main\ for dashboard and user pages
echo    - screenshots\plans\ for plan management
echo    - screenshots\billing\ for billing pages
echo    - screenshots\analytics\ for reports and analytics
echo    - screenshots\communication\ for email pages
echo    - screenshots\admin\ for admin panel
echo.
echo After taking screenshots, commit them to GitHub:
echo   git add screenshots/
echo   git commit -m "Add comprehensive screenshots"
echo   git push origin main
echo.
pause 