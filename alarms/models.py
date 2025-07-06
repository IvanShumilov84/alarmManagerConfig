from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class AlarmTable(models.Model):
    """Модель для таблиц аварийных сигналов"""
    name = models.CharField(max_length=100, verbose_name="Название таблицы")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Таблица аварий"
        verbose_name_plural = "Таблицы аварий"

    def __str__(self):
        return self.name

class AlarmConfig(models.Model):
    """Модель для конфигурации аварийных сигналов"""
    
    # Константы для выбора
    LOGIC_CHOICES = [
        ('discrete', 'Дискретное событие'),
        ('analog', 'Аналоговое событие'),
        ('change', 'Изменение события'),
    ]
    
    LIMIT_TYPE_CHOICES = [
        ('low', 'Ограничение снизу'),
        ('high', 'Ограничение сверху'),
        ('low_high', 'Ограничение снизу и сверху'),
    ]
    
    LIMIT_CONFIG_TYPE_CHOICES = [
        ('values', 'Значения пределов'),
        ('channels', 'Каналы пределов'),
    ]
    
    ALARM_CLASS_CHOICES = [
        ('error', 'Ошибка'),
        ('warn', 'Предупреждение'),
        ('info', 'Информирование'),
    ]
    
    CONFIRM_METHOD_CHOICES = [
        ('rep_ack', 'Квитирование деактивированной тревоги'),
    ]

    # Основные поля
    alarm_class = models.CharField(
        max_length=20, 
        choices=ALARM_CLASS_CHOICES,
        verbose_name="Класс тревоги"
    )
    table = models.ForeignKey(
        AlarmTable, 
        on_delete=models.CASCADE,
        related_name='alarms',
        verbose_name="Таблица сообщений"
    )
    logic = models.CharField(
        max_length=20, 
        choices=LOGIC_CHOICES,
        verbose_name="Способ наблюдения"
    )
    channel = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Имя канала"
    )
    
    # Поля для аналоговых сигналов
    limit_type = models.CharField(
        max_length=20, 
        choices=LIMIT_TYPE_CHOICES,
        blank=True,
        verbose_name="Тип ограничения"
    )
    limit_config_type = models.CharField(
        max_length=20,
        choices=LIMIT_CONFIG_TYPE_CHOICES,
        default='values',
        verbose_name="Тип настройки пределов"
    )
    low = models.FloatField(
        default=0.0,
        verbose_name="Нижний предел"
    )
    high = models.FloatField(
        default=0.0,
        verbose_name="Верхний предел"
    )
    
    # Поля для дискретных сигналов
    discrete_val = models.FloatField(
        default=0.0,
        verbose_name="Значение предела для дискретного сигнала"
    )
    
    # Общие поля
    msg = models.TextField(
        verbose_name="Текст сообщения"
    )
    hyst_low = models.FloatField(
        default=0.0,
        verbose_name="Гистерезис нижнего предела"
    )
    hyst_high = models.FloatField(
        default=0.0,
        verbose_name="Гистерезис верхнего предела"
    )
    ch_low = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Канал нижнего предела"
    )
    ch_high = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Канал верхнего предела"
    )
    confirm_method = models.CharField(
        max_length=20, 
        choices=CONFIRM_METHOD_CHOICES,
        default='manual',
        verbose_name="Способ подтверждения"
    )
    prior = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        default=500,
        verbose_name="Приоритет тревоги"
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Конфигурация аварии"
        verbose_name_plural = "Конфигурации аварий"
        ordering = ['alarm_class', 'prior']

    def __str__(self):
        return f"{self.alarm_class} - {self.msg[:50]}"
