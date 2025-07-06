#!/usr/bin/env python
"""
Скрипт для автозапуска Django сервера
Система управления аварийными сигналами
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    """Основная функция запуска сервера"""
    print("=" * 60)
    print("🚀 Система управления аварийными сигналами")
    print("=" * 60)
    
    # Определяем путь к manage.py
    script_dir = Path(__file__).parent
    manage_py = script_dir / "manage.py"
    
    if not manage_py.exists():
        print("❌ Ошибка: Файл manage.py не найден!")
        print(f"   Ожидаемый путь: {manage_py}")
        input("Нажмите Enter для выхода...")
        return
    
    print(f"📁 Рабочая директория: {script_dir}")
    print(f"🔧 Файл управления: {manage_py}")
    
    # Проверяем наличие базы данных
    db_file = script_dir / "db.sqlite3"
    if not db_file.exists():
        print("⚠️  База данных не найдена. Выполняем миграции...")
        try:
            subprocess.run([sys.executable, str(manage_py), "migrate"], 
                         check=True, cwd=script_dir)
            print("✅ Миграции выполнены успешно!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при выполнении миграций: {e}")
            input("Нажмите Enter для выхода...")
            return
    
    # Запускаем сервер
    print("\n🌐 Запуск веб-сервера...")
    print("📡 Сервер будет доступен по адресу: http://127.0.0.1:8000")
    print("🔄 Для остановки сервера нажмите Ctrl+C")
    print("-" * 60)
    
    try:
        # Открываем браузер через 3 секунды
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://127.0.0.1:8000')
                print("🌐 Браузер открыт автоматически")
            except:
                print("⚠️  Не удалось открыть браузер автоматически")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Запускаем Django сервер
        subprocess.run([sys.executable, str(manage_py), "runserver", "127.0.0.1:8000"], 
                      cwd=script_dir)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
    finally:
        print("\n👋 До свидания!")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 