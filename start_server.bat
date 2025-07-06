@echo off
chcp 65001 > nul
title Система управления аварийными сигналами

echo.
echo ============================================================
echo    Система управления аварийными сигналами
echo ============================================================
echo.

REM Проверяем наличие Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден в системе!
    echo Установите Python 3.8+ и добавьте его в PATH
    pause
    exit /b 1
)

REM Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
)

REM Активируем виртуальное окружение
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)

REM Выполняем миграции
echo Выполнение миграций базы данных...
python manage.py migrate
if errorlevel 1 (
    echo ОШИБКА: Не удалось выполнить миграции!
    pause
    exit /b 1
)

REM Запускаем сервер
echo.
echo Запуск веб-сервера...
echo Сервер будет доступен по адресу: http://127.0.0.1:8000
echo Для остановки сервера нажмите Ctrl+C
echo.
python run_server.py

pause 