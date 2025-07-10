#!/usr/bin/env python3
import os
import sys
import webbrowser
import threading
import time


def open_browser():
    """Открывает браузер с небольшой задержкой"""
    time.sleep(2)  # Ждем запуска сервера
    webbrowser.open("http://127.0.0.1:8000")


def main():
    # Устанавливаем рабочую директорию
    if getattr(sys, "frozen", False):
        # Если запущено из exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Если запущено из Python
        application_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(application_path)

    # Устанавливаем переменную окружения для Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alarm_manager.settings")

    # Исправляем sys.argv для Django
    sys.argv = ["manage.py", "runserver", "127.0.0.1:8000"]

    # Открываем браузер в отдельном потоке
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Запускаем Django
    try:
        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Ошибка запуска Django: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
