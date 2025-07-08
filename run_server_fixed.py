#!/usr/bin/env python
"""
Скрипт для автозапуска Django сервера (исправленная версия для PyInstaller)
Система управления аварийными сигналами
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

def get_base_path():
    """Получаем базовый путь для PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe (PyInstaller)
        return Path(sys._MEIPASS)
    else:
        # Если запущено как Python скрипт
        return Path(__file__).parent

def main():
    """Основная функция запуска сервера"""
    print("=" * 60)
    print("🚀 Система управления аварийными сигналами")
    print("=" * 60)
    
    # Определяем базовый путь
    base_path = get_base_path()
    print(f"📁 Базовый путь: {base_path}")
    
    # Определяем путь к manage.py
    manage_py = base_path / "manage.py"
    
    if not manage_py.exists():
        print("❌ Ошибка: Файл manage.py не найден!")
        print(f"   Ожидаемый путь: {manage_py}")
        print("   Доступные файлы:")
        for file in base_path.iterdir():
            print(f"     - {file.name}")
        input("Нажмите Enter для выхода...")
        return
    
    print(f"🔧 Файл управления: {manage_py}")
    
    # Проверяем наличие базы данных
    db_file = base_path / "db.sqlite3"
    if not db_file.exists():
        print("⚠️  База данных не найдена. Выполняем миграции...")
        try:
            # Используем sys.executable для запуска manage.py
            result = subprocess.run([
                sys.executable, str(manage_py), "migrate"
            ], check=True, cwd=base_path, capture_output=True, text=True)
            print("✅ Миграции выполнены успешно!")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при выполнении миграций: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            input("Нажмите Enter для выхода...")
            return
    
    # Запускаем сервер
    print("\n🌐 Запуск веб-сервера...")
    print("📡 Сервер будет доступен по адресу: http://127.0.0.1:8000")
    print("🔄 Для остановки сервера нажмите Ctrl+C")
    print("-" * 60)
    
    # Флаг для отслеживания состояния сервера
    server_started = threading.Event()
    
    def open_browser():
        """Функция для открытия браузера"""
        # Ждем запуска сервера или максимум 10 секунд
        if server_started.wait(timeout=10):
            time.sleep(2)  # Дополнительная задержка для стабилизации
            try:
                webbrowser.open('http://127.0.0.1:8000')
                print("🌐 Браузер открыт автоматически")
            except Exception as e:
                print(f"⚠️  Не удалось открыть браузер автоматически: {e}")
        else:
            print("⚠️  Сервер не запустился в течение 10 секунд")
    
    # Запускаем поток для открытия браузера
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Запускаем Django сервер
        print("🔄 Запуск Django сервера...")
        process = subprocess.Popen([
            sys.executable, str(manage_py), "runserver", "127.0.0.1:8000"
        ], cwd=base_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
           text=True, bufsize=1, universal_newlines=True)
        
        # Отмечаем, что сервер запущен
        server_started.set()
        
        # Выводим логи сервера
        for line in process.stdout:
            print(line.rstrip())
            if "Starting development server" in line:
                print("✅ Сервер успешно запущен!")
        
        # Ждем завершения процесса
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен пользователем")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
    finally:
        print("\n👋 До свидания!")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 