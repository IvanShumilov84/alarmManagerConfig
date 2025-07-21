from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AlarmTable(models.Model):
    """Модель для таблиц тревог"""

    table_number = models.IntegerField(
        unique=True, 
        verbose_name="Номер таблицы",
        help_text="Уникальный номер таблицы. При создании автоматически подставляется следующий доступный номер.",
        validators=[MinValueValidator(0, message="Номер таблицы не может быть меньше 0")]
    )
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название таблицы",
        help_text="Укажите уникальное название для таблицы тревог."
    )
    description = models.TextField(blank=True, verbose_name="Описание", help_text="Описание поможет понять назначение таблицы.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Таблица тревог"
        verbose_name_plural = "Таблицы тревог"
        ordering = ["table_number"]

    def __str__(self):
        return f"Таблица {self.table_number}: {self.name}"
    
    def can_be_deleted(self):
        """Проверяет, можно ли удалить таблицу"""
        return self.alarms.count() == 0
    
    def get_alarms_count(self):
        """Возвращает количество тревог в таблице"""
        return self.alarms.count()
    
    @classmethod
    def get_next_available_number(cls):
        """Возвращает следующий доступный номер таблицы"""
        existing_numbers = set(cls.objects.values_list('table_number', flat=True))
        next_number = 1
        while next_number in existing_numbers:
            next_number += 1
        return next_number


class AlarmConfig(models.Model):
    """Модель для конфигурации тревог"""

    # Основные поля
    channel = models.CharField(max_length=100, unique=True, verbose_name="Имя канала")
    msg = models.TextField(verbose_name="Текст сообщения")
    table = models.ForeignKey(
        AlarmTable,
        on_delete=models.PROTECT,
        related_name="alarms",
        verbose_name="Таблица тревог",
    )
    alarm_class = models.ForeignKey(
        "AlarmClass",
        on_delete=models.PROTECT,
        verbose_name="Класс тревоги",
        related_name="alarm_configs",
    )
    logic = models.ForeignKey(
        "Logic",
        on_delete=models.PROTECT,
        verbose_name="Способ наблюдения",
        related_name="alarm_configs",
    )
    confirm_method = models.ForeignKey(
        "ConfirmMethod",
        on_delete=models.PROTECT,
        verbose_name="Способ подтверждения",
        related_name="alarm_configs",
    )
    prior = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name="Приоритет тревоги",
        default=500,
    )

    # Поля для аналоговых сигналов
    limit_type = models.ForeignKey(
        "LimitType",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Тип ограничения",
        related_name="alarm_configs",
    )
    limit_config_type = models.ForeignKey(
        "LimitConfigType",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Тип настройки пределов",
        related_name="alarm_configs",
    )
    low = models.FloatField(null=True, blank=True, verbose_name="Нижний предел")
    high = models.FloatField(null=True, blank=True, verbose_name="Верхний предел")
    ch_low = models.CharField(
        null=True, blank=True, max_length=100, verbose_name="Канал нижнего предела"
    )
    ch_high = models.CharField(
        null=True, blank=True, max_length=100, verbose_name="Канал верхнего предела"
    )
    hyst_low = models.FloatField(
        null=True, blank=True, verbose_name="Гистерезис нижнего предела", default=0.0
    )
    hyst_high = models.FloatField(
        null=True, blank=True, verbose_name="Гистерезис верхнего предела", default=0.0
    )

    # Поля для дискретных сигналов
    discrete_val = models.FloatField(
        null=True, blank=True, verbose_name="Значение предела для дискретного сигнала"
    )

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Конфигурация тревоги"
        verbose_name_plural = "Конфигурации тревог"
        ordering = ["id"]

    def __str__(self):
        return f"{self.alarm_class} - {self.msg[:50]}"


class AlarmClass(models.Model):
    """Модель для класса тревоги"""
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Класс тревоги"
        verbose_name_plural = "Классы тревог"

    def __str__(self):
        return self.verbose_name_ru


class Logic(models.Model):
    """Модель для способа наблюдения"""
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Способ наблюдения"
        verbose_name_plural = "Способ наблюдения"

    def __str__(self):
        return self.verbose_name_ru


class ConfirmMethod(models.Model):
    """Модель для способа подтверждения"""
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Способ подтверждения"
        verbose_name_plural = "Способы подтверждения"

    def __str__(self):
        return self.verbose_name_ru


class LimitType(models.Model):
    """Модель для типа ограничения"""
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Тип ограничения"
        verbose_name_plural = "Типы ограничений"

    def __str__(self):
        return self.verbose_name_ru


class LimitConfigType(models.Model):
    """Модель для типа настройки пределов"""
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Тип настройки пределов"
        verbose_name_plural = "Типы настройки пределов"

    def __str__(self):
        return self.verbose_name_ru
