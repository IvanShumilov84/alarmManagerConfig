from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import connection


def ensure_reference_data(sender, **kwargs):
    """Заполняет справочники базовыми данными при миграции"""
    from alarms.models import (
        AlarmClass,
        Logic,
        ConfirmMethod,
        LimitType,
        LimitConfigType,
    )

    # Проверяем, существуют ли все необходимые таблицы
    required_tables = [
        'alarms_alarmclass',
        'alarms_logic', 
        'alarms_confirmmethod',
        'alarms_limittype',
        'alarms_limitconfigtype'
    ]
    
    with connection.cursor() as cursor:
        for table_name in required_tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=%s
            """, [table_name])
            if not cursor.fetchone():
                return  # Если хотя бы одна таблица не существует, пропускаем создание данных

    # Создаём записи для AlarmClass
    alarm_classes = [
        {"name": "error", "verbose_name_ru": "Авария"},
        {"name": "warn", "verbose_name_ru": "Предупреждение"},
        {"name": "info", "verbose_name_ru": "Информирование"},
    ]
    for data in alarm_classes:
        AlarmClass.objects.get_or_create(name=data["name"], defaults=data)

    # Создаём записи для Logic
    logics = [
        {"name": "discrete", "verbose_name_ru": "Дискретное событие"},
        {"name": "analog", "verbose_name_ru": "Аналоговое событие"},
        {"name": "change", "verbose_name_ru": "Изменение события"},
    ]
    for data in logics:
        Logic.objects.get_or_create(name=data["name"], defaults=data)

    # Создаём записи для ConfirmMethod
    confirm_methods = [
        {"name": "rep_ack", "verbose_name_ru": "Квитирование деактивированной тревоги"},
    ]
    for data in confirm_methods:
        ConfirmMethod.objects.get_or_create(name=data["name"], defaults=data)

    # Создаём записи для LimitType
    limit_types = [
        {"name": "low", "verbose_name_ru": "Ограничение снизу"},
        {"name": "high", "verbose_name_ru": "Ограничение сверху"},
        {"name": "low_high", "verbose_name_ru": "Ограничение снизу и сверху"},
    ]
    for data in limit_types:
        LimitType.objects.get_or_create(name=data["name"], defaults=data)

    # Создаём записи для LimitConfigType
    limit_config_types = [
        {"name": "values", "verbose_name_ru": "Значения пределов"},
        {"name": "channels", "verbose_name_ru": "Каналы пределов"},
    ]
    for data in limit_config_types:
        LimitConfigType.objects.get_or_create(name=data["name"], defaults=data)


class AlarmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "alarms"

    def ready(self):
        # Подключаем сигнал для автоматического заполнения справочников
        post_migrate.connect(ensure_reference_data, sender=self)
