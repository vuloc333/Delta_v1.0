@echo off
chcp 65001 >nul
echo ==========================================
echo GIT CLEANUP SCRIPT
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/4] Xóa file đã tracked nhưng nay trong .gitignore...
git rm -r --cached . 2>nul
git add . 2>nul
echo    Done!
echo.

echo [2/4] Xóa __pycache__ folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d" 2>nul
)
echo    Done!
echo.

echo [3/4] Xóa cache files...
del /s /q *.cache 2>nul
del /s /q labels.cache 2>nul
echo    Done!
echo.

echo [4/4] Kiểm tra kích thước repo...
git count-objects -vH
echo.

echo ==========================================
echo HOÀN THÀNH!
echo ==========================================
echo.
echo Chạy: git status để xem thay đổi
echo Chạy: git commit -m "Clean up ignored files" để commit
echo.
pause
