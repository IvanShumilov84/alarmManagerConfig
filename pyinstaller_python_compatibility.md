# Совместимость PyInstaller с версиями Python

## Поддерживаемые версии Python

**PyInstaller (версия 6.14.2) поддерживает Python 3.8-3.13**

### Подробности по версиям:

- **Python 3.8-3.13**: Полная поддержка
- **Python 3.14**: Бета-версии не поддерживаются
- **Python 3.10.0**: Содержит критическую ошибку, несовместимую с PyInstaller

### Требования к установке:

```bash
pip install pyinstaller
```

Для установки требуется Python версии от 3.8 до 3.13 (не включая 3.14).

## Платформы

PyInstaller тестируется и поддерживается на:
- **Windows** (32bit/64bit/ARM64) - Windows 8+
- **macOS** (x86_64/ARM64) - macOS 10.15+
- **Linux** (x86_64, aarch64, i686, ppc64le, s390x)

## Важные замечания

1. **Python 3.10.0**: Эта конкретная версия содержит баг, который делает её несовместимой с PyInstaller
2. **Python 3.14**: Бета-версии Python 3.14 официально не поддерживаются
3. **Кросс-компиляция**: PyInstaller не является кросс-компилятором - для создания приложения под Windows нужно запускать PyInstaller в Windows, для Linux - в Linux, и т.д.

## Источники информации

- Официальная документация PyInstaller: https://pyinstaller.org/
- PyPI страница: https://pypi.org/project/pyinstaller/
- Changelog: https://pyinstaller.org/en/stable/CHANGES.html

*Дата актуализации: январь 2025*