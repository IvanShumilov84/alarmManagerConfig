#!/usr/bin/env python
"""
Запуск Django сервера с открытием браузера только один раз (PyInstaller-friendly)
Система управления аварийными сигналами
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

def setup_django():
    """Настройка Django окружения."""
    base_path = get_base_path()
    sys.path.insert(0, str(base_path))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alarm_manager.settings')
    import django
    django.setup()
    return base_path

def get_base_path():
    """Получаем базовый путь для PyInstaller."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent

def run_migrations():
    """Выполнение миграций."""
    try:
        from django.core.management import execute_from_command_line
        print('sys.argv (migrate):', sys.argv)
        print('cwd (migrate):', os.getcwd())
        sys.argv = ['manage.py', 'migrate']
        execute_from_command_line(sys.argv)
        print("✅ Миграции выполнены успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграций: {e}")
        return False

def run_server():
    """Запуск Django сервера."""
    try:
        from django.core.management import execute_from_command_line
        print('sys.argv (runserver):', sys.argv)
        print('cwd (runserver):', os.getcwd())
        sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000']
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")

def open_browser_once():
    """Открывает браузер только один раз за сессию."""
    if os.environ.get('ALARM_MANAGER_BROWSER_OPENED') == '1':
        return
    os.environ['ALARM_MANAGER_BROWSER_OPENED'] = '1'
    time.sleep(3)
    try:
        webbrowser.open('http://127.0.0.1:8000')
        print("🌐 Браузер открыт автоматически")
    except Exception as e:
        print(f"⚠️  Не удалось открыть браузер автоматически: {e}")

def main():
    print("=" * 60)
    print("🚀 Система управления аварийными сигналами")
    print("=" * 60)
    print("🔧 Настройка Django...")
    base_path = setup_django()
    os.chdir(base_path)  # Важно для PyInstaller!
    print(f"📁 Базовый путь: {base_path}")
    # Диагностика путей и settings
    print('DJANGO_SETTINGS_MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE'))
    print('Содержимое base_path:', list(os.listdir(base_path)))
    print('manage.py существует:', os.path.exists('manage.py'))
    import importlib
    try:
        importlib.import_module('alarm_manager.settings')
        print('Импорт alarm_manager.settings: OK')
    except Exception as e:
        print('Ошибка импорта alarm_manager.settings:', e)
    db_file = base_path / "db.sqlite3"
    if not db_file.exists():
        print("⚠️  База данных не найдена. Выполняем миграции...")
        if not run_migrations():
            input("Нажмите Enter для выхода...")
            return
    print("\n🌐 Запуск веб-сервера...")
    print("📡 Сервер будет доступен по адресу: http://127.0.0.1:8000")
    print("🔄 Для остановки сервера нажмите Ctrl+C")
    print("-" * 60)
    browser_thread = threading.Thread(target=open_browser_once)
    browser_thread.daemon = True
    browser_thread.start()
    try:
        run_server()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        print("\n👋 До свидания!")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 