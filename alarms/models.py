from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# --- Кастомный QuerySet для soft delete ---
class SoftDeleteQuerySet(models.QuerySet):
    def deleted(self):
        """Только мягко удалённые записи"""
        return self.filter(deleted_at__isnull=False)

    def not_deleted(self):
        """Только не удалённые записи"""
        return self.filter(deleted_at__isnull=True)

    def restore(self):
        """Массовое восстановление записей"""
        return self.update(deleted_at=None)


# --- Менеджеры ---
class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).not_deleted()


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата удаления"
    )

    # Менеджеры
    objects = NotDeletedManager()  # Только не удалённые
    all_objects = AllObjectsManager()  # Все записи (в т.ч. удалённые)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Мягкое удаление записи - устанавливает deleted_at в текущее время"""
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


class AlarmTable(SoftDeleteModel):
    """Модель для таблиц тревог"""

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название таблицы"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Таблица тревог"
        verbose_name_plural = "Таблицы тревог"
        ordering = ["id"]

    def __str__(self):
        return self.name


class AlarmConfig(SoftDeleteModel):
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
        null=True, blank=True, verbose_name="Гистерезис нижнего предела"
    )
    hyst_high = models.FloatField(
        null=True, blank=True, verbose_name="Гистерезис верхнего предела"
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
