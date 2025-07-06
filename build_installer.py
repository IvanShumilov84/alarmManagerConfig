#!/usr/bin/env python
"""
Скрипт для сборки установщика с помощью Nuitka
Система управления аварийными сигналами
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Основная функция сборки"""
    print("=" * 60)
    print("🔨 Сборка установщика с помощью Nuitka")
    print("=" * 60)
    
    # Проверяем наличие Nuitka
    try:
        import nuitka
        print("✅ Nuitka найден")
    except ImportError:
        print("❌ Nuitka не установлен!")
        print("Установите: pip install nuitka")
        return
    
    # Создаем папку для сборки
    build_dir = Path("dist")
    if build_dir.exists():
        print("🗑️  Удаляем старую папку сборки...")
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # Также удаляем временные файлы Nuitka
    temp_dirs = ["run_server.build", "run_server.dist", "run_server.onefile-build"]
    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        if temp_path.exists():
            print(f"🗑️  Удаляем временную папку: {temp_dir}")
            shutil.rmtree(temp_path)
    
    print(f"📁 Папка сборки: {build_dir.absolute()}")
    
    # Команда сборки
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--include-package=django",
        "--include-package=rest_framework",
        "--include-package=alarm_manager",
        "--include-package=alarms",
        "--output-dir=dist",
        "--assume-yes-for-downloads",
        "--show-progress",
        "--show-memory",
        "--remove-output",
        "run_server.py"
    ]
    
    print("\n🚀 Начинаем сборку...")
    print(f"Команда: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # Запускаем сборку
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n✅ Сборка завершена успешно!")
            
            # Копируем необходимые файлы
            exe_dir = build_dir / "run_server.dist"
            if exe_dir.exists():
                print(f"📦 Исполняемый файл: {exe_dir}")
                
                # Копируем Django файлы
                files_to_copy = [
                    "manage.py",
                    "db.sqlite3",
                    "alarm_manager",
                    "alarms",
                    "templates",
                    "static"
                ]
                
                print("\n📋 Копирование файлов проекта...")
                for file_name in files_to_copy:
                    src = Path(file_name)
                    dst = exe_dir / file_name
                    
                    if src.exists():
                        if src.is_file():
                            shutil.copy2(src, dst)
                        else:
                            if dst.exists():
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        print(f"  ✅ {file_name}")
                    else:
                        print(f"  ⚠️  {file_name} (не найден)")
                
                # Создаем README для пользователя
                readme_content = """# Система управления аварийными сигналами

## Запуск приложения

1. Дважды кликните на файл `run_server.exe`
2. Дождитесь запуска сервера
3. Браузер откроется автоматически по адресу http://127.0.0.1:8000

## Остановка сервера

Нажмите Ctrl+C в окне консоли или закройте окно.

## Структура файлов

- `run_server.exe` - главный исполняемый файл
- `manage.py` - файл управления Django
- `db.sqlite3` - база данных
- `alarm_manager/` - настройки проекта
- `alarms/` - приложение аварийных сигналов
- `templates/` - HTML шаблоны
- `static/` - статические файлы

## Возможности

- ✅ Создание и управление таблицами аварийных сигналов
- ✅ Настройка аварийных сигналов с различными типами логики
- ✅ Экспорт конфигурации в JSON файл
- ✅ Современный и удобный интерфейс

## Поддержка

При возникновении проблем проверьте:
1. Антивирус не блокирует приложение
2. Порт 8000 не занят другими приложениями
3. Браузер поддерживает современные веб-стандарты
"""
                
                readme_file = exe_dir / "README.txt"
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                print(f"\n📖 Создан файл README: {readme_file}")
                print(f"\n🎉 Установщик готов!")
                print(f"📁 Расположение: {exe_dir.absolute()}")
                print(f"🚀 Для запуска: {exe_dir / 'run_server.exe'}")
                
            else:
                print("❌ Папка с исполняемым файлом не найдена!")
                
        else:
            print(f"❌ Ошибка сборки (код: {result.returncode})")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    print("\n" + "=" * 60)
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 