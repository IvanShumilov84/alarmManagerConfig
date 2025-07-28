# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AlarmTable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
            ],
            options={
                "verbose_name": "Таблица тревог",
                "verbose_name_plural": "Таблицы тревог",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="AlarmConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("channel", models.CharField(max_length=50, verbose_name="Канал")),
                ("msg", models.CharField(max_length=200, verbose_name="Сообщение")),
                (
                    "alarm_class",
                    models.CharField(max_length=50, verbose_name="Класс тревоги"),
                ),
                ("logic", models.CharField(max_length=50, verbose_name="Логика")),
                (
                    "confirm_method",
                    models.CharField(
                        max_length=50, verbose_name="Способ подтверждения"
                    ),
                ),
                ("prior", models.IntegerField(verbose_name="Приоритет")),
                (
                    "limit_type",
                    models.CharField(max_length=50, verbose_name="Тип лимита"),
                ),
                (
                    "limit_config_type",
                    models.CharField(
                        max_length=50, verbose_name="Тип конфигурации лимита"
                    ),
                ),
                ("low", models.FloatField(verbose_name="Нижний лимит")),
                ("high", models.FloatField(verbose_name="Верхний лимит")),
                ("ch_low", models.FloatField(verbose_name="Нижний лимит канала")),
                ("ch_high", models.FloatField(verbose_name="Верхний лимит канала")),
                ("hyst_low", models.FloatField(verbose_name="Нижний гистерезис")),
                ("hyst_high", models.FloatField(verbose_name="Верхний гистерезис")),
                (
                    "discrete_val",
                    models.CharField(max_length=50, verbose_name="Дискретное значение"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="alarms.alarmtable",
                        verbose_name="Таблица",
                    ),
                ),
            ],
            options={
                "verbose_name": "Конфигурация аварии",
                "verbose_name_plural": "Конфигурации аварий",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="UserColumnPreferences",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_id",
                    models.IntegerField(
                        help_text="ID пользователя для которого сохраняются настройки",
                        verbose_name="ID пользователя",
                    ),
                ),
                (
                    "page_type",
                    models.CharField(
                        help_text="Тип страницы (alarms, tables, etc.)",
                        max_length=50,
                        verbose_name="Тип страницы",
                    ),
                ),
                (
                    "column_order",
                    models.JSONField(
                        default=list,
                        help_text="JSON массив с порядком столбцов",
                        verbose_name="Порядок столбцов",
                    ),
                ),
                (
                    "sticky_columns",
                    models.IntegerField(
                        default=0,
                        help_text="Количество закрепленных столбцов (0 = нет закрепления)",
                        verbose_name="Количество закрепленных столбцов",
                    ),
                ),
                (
                    "sort_settings",
                    models.JSONField(
                        default=dict,
                        help_text="JSON объект с настройками сортировки",
                        verbose_name="Настройки сортировки",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
            ],
            options={
                "verbose_name": "Настройки таблицы пользователя",
                "verbose_name_plural": "Настройки таблиц пользователей",
                "ordering": ["user_id", "page_type"],
                "unique_together": {("user_id", "page_type")},
            },
        ),
    ]
