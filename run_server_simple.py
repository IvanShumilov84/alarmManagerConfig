#!/usr/bin/env python
"""
Простой запуск Django сервера (без автобраузера)
Система управления аварийными сигналами
"""

import os
import sys
from pathlib import Path

def setup_django():
    """Настройка Django окружения"""
    # Добавляем текущую директорию в Python path
    base_path = get_base_path()
    sys.path.insert(0, str(base_path))
    
    # Устанавливаем переменную окружения
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alarm_manager.settings')
    
    # Импортируем Django
    import django
    django.setup()
    
    return base_path

def get_base_path():
    """Получаем базовый путь для PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe (PyInstaller)
        return Path(sys._MEIPASS)
    else:
        # Если запущено как Python скрипт
        return Path(__file__).parent

def run_migrations():
    """Выполнение миграций"""
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Миграции выполнены успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграций: {e}")
        return False

def run_server():
    """Запуск Django сервера"""
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")

def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 Система управления аварийными сигналами")
    print("=" * 60)
    
    # Настраиваем Django
    print("🔧 Настройка Django...")
    base_path = setup_django()
    print(f"📁 Базовый путь: {base_path}")
    
    # Проверяем базу данных
    db_file = base_path / "db.sqlite3"
    if not db_file.exists():
        print("⚠️  База данных не найдена. Выполняем миграции...")
        if not run_migrations():
            input("Нажмите Enter для выхода...")
            return
    
    # Запускаем сервер
    print("\n🌐 Запуск веб-сервера...")
    print("📡 Сервер будет доступен по адресу: http://127.0.0.1:8000")
    print("🌐 Откройте браузер и перейдите по адресу выше")
    print("🔄 Для остановки сервера нажмите Ctrl+C")
    print("-" * 60)
    
    try:
        # Запускаем сервер
        run_server()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        print("\n👋 До свидания!")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 