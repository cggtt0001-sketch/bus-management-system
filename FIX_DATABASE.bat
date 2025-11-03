@echo off
echo ====================================
echo 🔧 Database Fix for Bus Management
echo ====================================
echo.
echo This will fix the "no such column: buses.location_lat" error
echo.
pause

python FIX_YOUR_DATABASE.py

echo.
echo ====================================
echo ✅ Fix complete!
echo ====================================
echo.
echo Now run your Flask app with: python run.py
echo Then visit: http://localhost:5000/dashboard/map
echo.
pause