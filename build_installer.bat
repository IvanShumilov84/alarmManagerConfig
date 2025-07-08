@echo off
chcp 65001 >nul
echo ================================================
echo Сборка установщика через PyInstaller
echo ================================================
echo.

REM Активируем виртуальное окружение
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Запускаем сборку
echo 🔨 Запуск сборки...
python build_pyinstaller.py

echo.
echo ✅ Сборка завершена!
echo 📁 Установщик: AlarmManager_Setup.zip
echo.
pause 