@echo off
echo ======================================
echo    SwiftDrop - Quick Deploy Utility
echo ======================================
echo.

echo Collecting static files...
python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production

echo Running database migrations...
python manage.py migrate --settings=Nagaribashi_express.settings_production

echo.
echo Ready for deployment!
echo.
echo Next steps:
echo 1. Verify your target host environment (Render, Railway, VPS, PythonAnywhere)
echo 2. Review DEPLOYMENT_GUIDE.md
echo 3. Configure production environment variables in .env
echo 4. Start the WSGI server (e.g., gunicorn Nagaribashi_express.wsgi)
echo.
echo Author: Rifat Bin Alam
echo Contact: rifat5566123@gmail.com
echo GitHub: https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp
pause
