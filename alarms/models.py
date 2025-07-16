from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AlarmTable(models.Model):
    """Модель для таблиц аварийных сигналов"""

    name = models.CharField(max_length=100, verbose_name="Название таблицы")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата удаления"
    )

    class Meta:
        verbose_name = "Таблица аварий"
        verbose_name_plural = "Таблицы аварий"

    def __str__(self):
        return self.name

    def soft_delete(self):
        """Мягкое удаление записи - устанавливает deleted_at в текущее время"""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Восстановление записи - очищает deleted_at"""
        self.deleted_at = None
        self.save()

    def delete(self, *args, **kwargs):
        """Переопределяем стандартное удаление для предотвращения физического удаления"""
        # Не вызываем super().delete() - блокируем физическое удаление
        return 0  # Возвращаем 0 удаленных записей


class AlarmConfig(models.Model):
    """Модель для конфигурации аварийных сигналов"""

    # Константы для выбора
    LOGIC_CHOICES = [
        ("discrete", "Дискретное событие"),
        ("analog", "Аналоговое событие"),
        ("change", "Изменение события"),
    ]

    LIMIT_TYPE_CHOICES = [
        ("low", "Ограничение снизу"),
        ("high", "Ограничение сверху"),
        ("low_high", "Ограничение снизу и сверху"),
    ]

    LIMIT_CONFIG_TYPE_CHOICES = [
        ("values", "Значения пределов"),
        ("channels", "Каналы пределов"),
    ]

    ALARM_CLASS_CHOICES = [
        ("error", "Ошибка"),
        ("warn", "Предупреждение"),
        ("info", "Информирование"),
    ]

    CONFIRM_METHOD_CHOICES = [
        ("rep_ack", "Квитирование деактивированной тревоги"),
    ]

    # Основные поля
    alarm_class = models.ForeignKey(
        "AlarmClass",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Класс тревоги",
        related_name="alarm_configs",
    )
    table = models.ForeignKey(
        AlarmTable,
        on_delete=models.CASCADE,
        related_name="alarms",
        verbose_name="Таблица сообщений",
    )
    logic = models.ForeignKey(
        "Logic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Способ наблюдения",
        related_name="alarm_configs",
    )
    channel = models.CharField(max_length=100, blank=True, verbose_name="Имя канала")

    # Поля для аналоговых сигналов
    limit_type = models.ForeignKey(
        "LimitType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип ограничения",
        related_name="alarm_configs",
    )
    limit_config_type = models.ForeignKey(
        "LimitConfigType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип настройки пределов",
        related_name="alarm_configs",
    )
    low = models.FloatField(default=0.0, verbose_name="Нижний предел")
    high = models.FloatField(default=0.0, verbose_name="Верхний предел")

    # Поля для дискретных сигналов
    discrete_val = models.FloatField(
        default=0.0, verbose_name="Значение предела для дискретного сигнала"
    )

    # Общие поля
    msg = models.TextField(verbose_name="Текст сообщения")
    hyst_low = models.FloatField(default=0.0, verbose_name="Гистерезис нижнего предела")
    hyst_high = models.FloatField(
        default=0.0, verbose_name="Гистерезис верхнего предела"
    )
    ch_low = models.CharField(
        max_length=100, blank=True, verbose_name="Канал нижнего предела"
    )
    ch_high = models.CharField(
        max_length=100, blank=True, verbose_name="Канал верхнего предела"
    )
    confirm_method = models.ForeignKey(
        "ConfirmMethod",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Способ подтверждения",
        related_name="alarm_configs",
    )
    prior = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        default=500,
        verbose_name="Приоритет тревоги",
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата удаления"
    )

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Конфигурация аварии"
        verbose_name_plural = "Конфигурации аварий"
        ordering = ["alarm_class", "prior"]

    def __str__(self):
        return f"{self.alarm_class} - {self.msg[:50]}"

    def soft_delete(self):
        """Мягкое удаление записи - устанавливает deleted_at в текущее время"""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Восстановление записи - очищает deleted_at"""
        self.deleted_at = None
        self.save()

    def delete(self, *args, **kwargs):
        """Переопределяем стандартное удаление для предотвращения физического удаления"""
        # Не вызываем super().delete() - блокируем физическое удаление
        return 0  # Возвращаем 0 удаленных записей


class AlarmClass(models.Model):
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Класс аварии"
        verbose_name_plural = "Классы аварий"

    def __str__(self):
        return self.verbose_name_ru


class Logic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Логика"
        verbose_name_plural = "Логики"

    def __str__(self):
        return self.verbose_name_ru


class ConfirmMethod(models.Model):
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Способ подтверждения"
        verbose_name_plural = "Способы подтверждения"

    def __str__(self):
        return self.verbose_name_ru


class LimitType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Тип ограничения"
        verbose_name_plural = "Типы ограничений"

    def __str__(self):
        return self.verbose_name_ru


class LimitConfigType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    verbose_name_ru = models.CharField(max_length=64)

    class Meta:
        ordering = ["id"]
        verbose_name = "Тип настройки пределов"
        verbose_name_plural = "Типы настройки пределов"

    def __str__(self):
        return self.verbose_name_ru
