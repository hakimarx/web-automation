@echo off
echo ========================================
echo Setup Aplikasi Otomatisasi Web
echo ========================================
echo.

echo Menginstall dependencies...
pip install -r requirements.txt

echo.
echo Menginstall Playwright Chromium...
playwright install chromium

echo.
echo ========================================
echo Setup selesai!
echo.
echo Selanjutnya:
echo 1. Edit config.json dengan konfigurasi Anda
echo 2. Setup Gmail App Password
echo 3. Jalankan: python web_automation.py
echo ========================================
pause

