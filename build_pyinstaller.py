#!/usr/bin/env python3
"""Скрипт для сборки Django-приложения в exe-файл с помощью PyInstaller."""

import os
import sys
import subprocess
import shutil


def create_run_server_script():
    """Создает скрипт для запуска Django-сервера"""
    script_content = '''#!/usr/bin/env python3
import os
import sys
import webbrowser
import threading
import time

def open_browser():
    """Открывает браузер с небольшой задержкой"""
    time.sleep(2)  # Ждем запуска сервера
    webbrowser.open('http://127.0.0.1:8000')

def main():
    # Устанавливаем рабочую директорию
    if getattr(sys, 'frozen', False):
        # Если запущено из exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Если запущено из Python
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(application_path)
    
    # Устанавливаем переменную окружения для Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alarm_manager.settings')
    
    # Исправляем sys.argv для Django
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000']
    
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

if __name__ == '__main__':
    main()
'''

    with open("run_server.py", "w", encoding="utf-8") as f:
        f.write(script_content)

    print("✓ Создан скрипт run_server.py")


def create_spec_file():
    """Создает spec-файл для PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('manage.py', '.'),
        ('db.sqlite3', '.'),
        ('templates', 'templates'),
        ('static', 'static'),
        ('alarm_manager', 'alarm_manager'),
        ('alarms', 'alarms'),
    ],
    hiddenimports=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'alarms',
        'alarm_manager.settings',
        'alarm_manager.urls',
        'alarm_manager.wsgi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AlarmManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""

    with open("AlarmManager.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✓ Создан spec-файл AlarmManager.spec")


def build_executable():
    """Собирает exe-файл с помощью PyInstaller"""
    print("🔨 Начинаю сборку exe-файла...")

    # Проверяем, установлен ли PyInstaller
    try:
        import PyInstaller

        print(f"✓ PyInstaller версии {PyInstaller.__version__} найден")
    except ImportError:
        print("❌ PyInstaller не установлен. Устанавливаю...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )
        print("✓ PyInstaller установлен")

    # Удаляем старые папки сборки
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Удалена папка {folder}")

    # Запускаем PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "AlarmManager.spec", "--noconfirm"]
    print(f"Выполняю команду: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Сборка завершена успешно!")
        exe_path = os.path.abspath("dist/AlarmManager.exe")
        print(f"📁 Exe-файл находится в: {exe_path}")
    else:
        print("❌ Ошибка при сборке:")
        print(result.stderr)
        return False

    return True


def main():
    """Основная функция"""
    print("🚀 Запуск сборки Django-приложения в exe-файл")
    print("=" * 50)

    # Проверяем наличие необходимых файлов
    required_files = ["manage.py", "db.sqlite3", "alarm_manager/settings.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден!")
            return False

    print("✓ Все необходимые файлы найдены")

    # Создаем скрипт запуска
    create_run_server_script()

    # Создаем spec-файл
    create_spec_file()

    # Собираем exe-файл
    if build_executable():
        print("\n🎉 Сборка завершена!")
        print("\n📋 Инструкции по использованию:")
        print("1. Exe-файл: dist/AlarmManager.exe")
        print("2. Запустите exe-файл двойным кликом")
        print("3. Автоматически откроется браузер с приложением")
        print("4. Для остановки закройте окно консоли")
        # Копируем manage.py в dist/AlarmManager/
        import shutil

        dist_dir = os.path.join("dist", "AlarmManager")
        src_manage = "manage.py"
        dst_manage = os.path.join(dist_dir, "manage.py")
        if os.path.exists(dist_dir):
            shutil.copy2(src_manage, dst_manage)
            print(f"✓ manage.py скопирован в {dst_manage}")
        else:
            print(f"❌ Папка {dist_dir} не найдена!")
    else:
        print("\n❌ Сборка не удалась!")


if __name__ == "__main__":
    main()
