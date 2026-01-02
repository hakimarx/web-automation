@echo off
echo ========================================
echo Upload ke GitHub
echo ========================================
echo.
echo Pastikan Anda sudah:
echo 1. Login ke GitHub di browser
echo 2. Membuat repository baru di https://github.com/new
echo 3. Mengetahui URL repository (contoh: https://github.com/USERNAME/web_automation.git)
echo.
echo Masukkan URL repository GitHub Anda:
echo (contoh: https://github.com/USERNAME/web_automation.git)
set /p REPO_URL="Repository URL: "

if "%REPO_URL%"=="" (
    echo Error: URL repository tidak boleh kosong!
    pause
    exit /b 1
)

echo.
echo Menambahkan remote repository...
git remote add origin %REPO_URL%
if errorlevel 1 (
    echo Warning: Remote sudah ada, menggunakan remote yang ada...
    git remote set-url origin %REPO_URL%
)

echo.
echo Mengubah branch ke main...
git branch -M main

echo.
echo Mengupload kode ke GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Gagal upload ke GitHub
    echo ========================================
    echo.
    echo Kemungkinan penyebab:
    echo 1. Belum login ke GitHub
    echo 2. URL repository salah
    echo 3. Repository belum dibuat di GitHub
    echo 4. Belum set up authentication (password/token)
    echo.
    echo Jika menggunakan token, gunakan format:
    echo https://TOKEN@github.com/USERNAME/web_automation.git
    echo.
) else (
    echo.
    echo ========================================
    echo BERHASIL! Kode sudah diupload ke GitHub
    echo ========================================
    echo.
)

pause

