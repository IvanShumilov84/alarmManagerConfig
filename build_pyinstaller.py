#!/usr/bin/env python
"""
Скрипт для создания установщика через PyInstaller
Система управления аварийными сигналами
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Основная функция сборки"""
    print("=" * 60)
    print("🔨 Создание установщика через PyInstaller")
    print("=" * 60)
    
    # Определяем пути
    project_dir = Path(__file__).parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    # Очищаем предыдущие сборки
    print("🧹 Очистка предыдущих сборок...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Создаем spec файл для PyInstaller
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_server_one_browser.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('manage.py', '.'),
        ('db.sqlite3', '.'),
        ('requirements.txt', '.'),
        ('alarm_manager', 'alarm_manager'),
        ('alarms', 'alarms'),
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'alarms',
        'alarm_manager',
        'alarm_manager.settings',
        'alarm_manager.urls',
        'alarm_manager.wsgi',
        'alarms.models',
        'alarms.views',
        'alarms.admin',
        'alarms.urls',
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
'''
    
    # Сохраняем spec файл
    spec_file = project_dir / "AlarmManager.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"📝 Создан spec файл: {spec_file}")
    
    # Запускаем PyInstaller
    print("\n🔨 Запуск PyInstaller...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ], check=True, capture_output=True, text=True)
        
        print("✅ PyInstaller выполнен успешно!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка PyInstaller: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return
    
    # Создаем README для установщика
    readme_content = '''# Система управления аварийными сигналами

## Установка и запуск

1. Распакуйте архив в удобное место
2. Запустите файл `AlarmManager.exe`
3. Дождитесь запуска сервера (появится сообщение "Сервер будет доступен по адресу: http://127.0.0.1:8000")
4. Браузер откроется автоматически, или перейдите по адресу http://127.0.0.1:8000

## Возможные проблемы

- Если браузер не открылся автоматически, откройте его вручную и перейдите по адресу http://127.0.0.1:8000
- Для остановки сервера нажмите Ctrl+C в окне консоли
- При первом запуске может потребоваться время для инициализации базы данных

## Системные требования

- Windows 10/11
- Минимум 100 МБ свободного места
- Доступ к интернету для первого запуска (загрузка зависимостей)

## Поддержка

При возникновении проблем обратитесь к разработчику.
'''
    
    readme_file = dist_dir / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📖 Создан README: {readme_file}")
    
    # Создаем batch файл для удобного запуска
    batch_content = '''@echo off
chcp 65001 >nul
echo ================================================
echo Система управления аварийными сигналами
echo ================================================
echo.
echo Запуск приложения...
echo.
AlarmManager.exe
pause
'''
    
    batch_file = dist_dir / "Запуск_приложения.bat"
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"📝 Создан batch файл: {batch_file}")
    
    # Создаем архив
    print("\n📦 Создание архива...")
    import zipfile
    
    archive_name = "AlarmManager_Setup.zip"
    archive_path = project_dir / archive_name
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
                print(f"  📄 Добавлен: {arcname}")
    
    print(f"\n✅ Установщик создан успешно!")
    print(f"📁 Расположение: {archive_path}")
    print(f"📊 Размер: {archive_path.stat().st_size / (1024*1024):.1f} МБ")
    
    # Очищаем временные файлы
    print("\n🧹 Очистка временных файлов...")
    if spec_file.exists():
        spec_file.unlink()
    
    print("\n🎉 Готово! Установщик готов к распространению.")

if __name__ == "__main__":
    main() 