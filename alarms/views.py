"""
AlarmManagerConfig - Views для управления тревогами

КОНТЕКСТ РАЗРАБОТКИ:
- Мигрировали с кастомного JavaScript на AG Grid
- Страница alarms отображает все 18 столбцов из модели AlarmConfig
- Адаптивное отображение: 18 столбцов на desktop/tablet, 5 на mobile
- Используется гибридное хранение настроек (localStorage + SQLite БД)

ПОСЛЕДНИЕ ИЗМЕНЕНИЯ:
- Добавлены все поля модели в AlarmConfigListView.get_context_data()
- Исправлен импорт csrf_exempt
- Обновлена конфигурация AG Grid для полного отображения данных

СЛЕДУЮЩИЕ ШАГИ:
- Реализовать UserColumnPreferences для сохранения настроек в БД
- Добавить экспорт данных
- Оптимизировать производительность AG Grid
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.utils.safestring import mark_safe
from .models import (
    AlarmConfig,
    AlarmTable,
    AlarmClass,
    Logic,
    ConfirmMethod,
    LimitType,
    LimitConfigType,
)
from .forms import AlarmConfigForm, AlarmTableForm


class AlarmTableListView(ListView):
    """Представление для списка таблиц аварий с AG Grid"""

    model = AlarmTable
    template_name = "alarms/table_list.html"
    context_object_name = "tables"

    def get_queryset(self):
        """Получаем queryset с подсчетом тревог для каждой таблицы"""
        return (
            AlarmTable.objects.all()
            .annotate(alarms_count=Count("alarms"))
            .order_by("table_number")
        )

    def get_context_data(self, **kwargs):
        """Добавляем базовые параметры в контекст"""
        context = super().get_context_data(**kwargs)
        return context


class AlarmTableCreateView(CreateView):
    """Представление для создания новой таблицы тревог"""

    model = AlarmTable
    form_class = AlarmTableForm
    template_name = "alarms/table_form.html"
    success_url = reverse_lazy("alarms:table_list")

    def get_initial(self):
        """Автоматически подставляем следующий доступный номер таблицы"""
        initial = super().get_initial()
        initial["table_number"] = AlarmTable.get_next_available_number()
        return initial

    def get_context_data(self, **kwargs):
        """Добавляем минимальное значение номера таблицы в контекст"""
        context = super().get_context_data(**kwargs)
        context["min_table_number"] = AlarmTable.get_min_table_number()

        return context


class AlarmTableUpdateView(UpdateView):
    """Представление для редактирования таблицы тревог"""

    model = AlarmTable
    form_class = AlarmTableForm
    template_name = "alarms/table_form.html"
    success_url = reverse_lazy("alarms:table_list")

    def get_context_data(self, **kwargs):
        """Добавляем минимальное значение номера таблицы в контекст"""
        context = super().get_context_data(**kwargs)
        context["min_table_number"] = AlarmTable.get_min_table_number()

        return context


class AlarmTableDeleteView(View):
    """Представление для удаления таблицы тревог"""

    def get(self, request, pk):
        """Показываем форму подтверждения удаления"""
        table = get_object_or_404(AlarmTable, pk=pk)
        return render(request, "alarms/table_confirm_delete.html", {"object": table})

    def post(self, request, pk):
        """Физическое удаление таблицы тревог"""
        table = get_object_or_404(AlarmTable, pk=pk)

        # Проверяем, можно ли удалить таблицу
        if not table.can_be_deleted():
            messages.error(
                request,
                f"Невозможно удалить таблицу '{table.name}'. В ней содержится {table.get_alarms_count()} тревог. "
                "Сначала удалите все тревоги из таблицы.",
            )
            return HttpResponseRedirect(reverse_lazy("alarms:table_list"))

        table.delete()
        messages.success(request, "Таблица тревог успешно удалена!")
        return HttpResponseRedirect(reverse_lazy("alarms:table_list"))


class AlarmConfigListView(ListView):
    """Представление для списка конфигураций аварий с AG Grid"""

    model = AlarmConfig
    template_name = "alarms/alarm_list.html"
    context_object_name = "alarms"

    def get_queryset(self):
        """Получаем queryset с оптимизированными запросами"""
        return (
            AlarmConfig.objects.all()
            .select_related(
                "alarm_class",
                "logic",
                "confirm_method",
                "limit_type",
                "limit_config_type",
                "table",
            )
            .order_by("alarm_class__verbose_name_ru", "prior", "channel")
        )

    def get_context_data(self, **kwargs):
        """Добавляем данные для AG Grid в контекст"""
        context = super().get_context_data(**kwargs)

        # Подготавливаем данные для AG Grid
        alarm_data = []
        for alarm in self.get_queryset():
            alarm_data.append(
                {
                    "id": alarm.id,
                    "channel": alarm.channel or "",
                    "message": alarm.msg or "",
                    "table": (
                        f"{alarm.table.table_number}: {alarm.table.name}"
                        if alarm.table
                        else ""
                    ),
                    "alarm_class": (
                        alarm.alarm_class.verbose_name_ru if alarm.alarm_class else ""
                    ),
                    "logic": alarm.logic.verbose_name_ru if alarm.logic else "",
                    "confirm_method": (
                        alarm.confirm_method.verbose_name_ru
                        if alarm.confirm_method
                        else ""
                    ),
                    "priority": alarm.prior or 0,
                    "limit_type": (
                        alarm.limit_type.verbose_name_ru if alarm.limit_type else ""
                    ),
                    "limit_config_type": (
                        alarm.limit_config_type.verbose_name_ru
                        if alarm.limit_config_type
                        else ""
                    ),
                    "low_limit": alarm.low or 0,
                    "high_limit": alarm.high or 0,
                    "hyst_low": alarm.hyst_low or 0,
                    "hyst_high": alarm.hyst_high or 0,
                    "discrete_val": alarm.discrete_val or 0,
                    "ch_low": alarm.ch_low or "",
                    "ch_high": alarm.ch_high or "",
                    "created_at": (
                        alarm.created_at.strftime("%Y-%m-%d %H:%M")
                        if alarm.created_at
                        else ""
                    ),
                    "updated_at": (
                        alarm.updated_at.strftime("%Y-%m-%d %H:%M")
                        if alarm.updated_at
                        else ""
                    ),
                }
            )

        context["alarm_data"] = mark_safe(json.dumps(alarm_data, ensure_ascii=False))

        # Справочные данные для фильтров
        context["alarm_classes"] = list(
            AlarmClass.objects.values_list("verbose_name_ru", flat=True)
        )
        context["logics"] = list(
            Logic.objects.values_list("verbose_name_ru", flat=True)
        )
        context["confirm_methods"] = list(
            ConfirmMethod.objects.values_list("verbose_name_ru", flat=True)
        )
        context["limit_types"] = list(
            LimitType.objects.values_list("verbose_name_ru", flat=True)
        )
        context["limit_config_types"] = list(
            LimitConfigType.objects.values_list("verbose_name_ru", flat=True)
        )

        return context


class AlarmTableDetailView(ListView):
    """Представление для отображения аварий конкретной таблицы"""

    model = AlarmConfig
    template_name = "alarms/table_detail.html"
    context_object_name = "alarms"
    paginate_by = 20

    def get_queryset(self):
        """Получаем аварии только для конкретной таблицы с сортировкой по русским названиям"""
        from django.db.models.functions import Lower

        self.table = get_object_or_404(AlarmTable, pk=self.kwargs["table_id"])
        queryset = AlarmConfig.objects.filter(table=self.table).select_related(
            "alarm_class", "logic"
        )

        # Создаем аннотации для сортировки по русским названиям
        queryset = queryset.annotate(
            alarm_class_display=Lower("alarm_class__verbose_name_ru"),
            logic_display=Lower("logic__verbose_name_ru"),
            channel_lower=Lower("channel"),
        )

        # Групповая сортировка: сначала по классу, затем по приоритету, затем по каналу
        return queryset.order_by("alarm_class_display", "prior", "channel_lower")

    def get_context_data(self, **kwargs):
        """Добавляем информацию о таблице в контекст"""
        context = super().get_context_data(**kwargs)
        context["table"] = self.table

        return context


class AlarmConfigCreateView(CreateView):
    """Представление для создания новой конфигурации аварии"""

    model = AlarmConfig
    form_class = AlarmConfigForm
    template_name = "alarms/alarm_form.html"
    success_url = reverse_lazy("alarms:alarm_list")

    def dispatch(self, request, *args, **kwargs):
        if not AlarmTable.objects.exists():
            messages.error(
                request,
                'Вы перенаправлены на страницу "Таблицы тревог", так как нельзя создать тревогу: нет ни одной таблицы тревог.',
            )
            return redirect("alarms:table_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Тревога успешно создана!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Добавляем отладочную информацию
        print("Form errors:", form.errors)
        print("Form data:", form.data)
        return super().form_invalid(form)


class AlarmConfigUpdateView(UpdateView):
    """Представление для редактирования конфигурации аварии"""

    model = AlarmConfig
    form_class = AlarmConfigForm
    template_name = "alarms/alarm_form.html"
    success_url = reverse_lazy("alarms:alarm_list")

    def form_valid(self, form):
        messages.success(self.request, "Тревога успешно обновлена!")
        return super().form_valid(form)


class AlarmConfigDeleteView(View):
    """Представление для удаления конфигурации аварии"""

    def get(self, request, pk):
        """Показываем форму подтверждения удаления"""
        alarm = get_object_or_404(AlarmConfig, pk=pk)
        return render(request, "alarms/alarm_confirm_delete.html", {"object": alarm})

    def post(self, request, pk):
        """Физическое удаление аварийного сигнала"""
        alarm = get_object_or_404(AlarmConfig, pk=pk)
        alarm.delete()
        messages.success(request, "Тревога успешно удалена!")
        return HttpResponseRedirect(reverse_lazy("alarms:alarm_list"))


def get_tables_count():
    """Возвращает количество таблиц тревог"""
    return AlarmTable.objects.all().count()


def get_alarms_count():
    """Возвращает количество тревог"""
    return AlarmConfig.objects.all().count()


def get_recent_alarms():
    """Возвращает последние 5 тревог"""
    from django.db.models.functions import Lower

    return (
        AlarmConfig.objects.all()
        .select_related("alarm_class")
        .annotate(alarm_class_display=Lower("alarm_class__verbose_name_ru"))
        .order_by("-created_at", "alarm_class_display", "prior")[:5]
    )


def sidebar_data(request):
    """Возвращает данные для сайдбара"""
    context = {
        "sidebar_tables_count": get_tables_count(),
        "sidebar_alarms_count": get_alarms_count(),
    }
    return render(request, "base.html", context)


def dashboard(request):
    """Главная страница приложения"""
    context = {
        "tables_count": get_tables_count(),
        "alarms_count": get_alarms_count(),
        "recent_alarms": get_recent_alarms(),
    }
    return render(request, "alarms/dashboard.html", context)


@csrf_exempt
def export_json(request):
    """Экспорт конфигураций аварий в JSON файл"""
    if request.method == "POST":
        try:
            # Получаем все конфигурации аварий с сортировкой по русским названиям
            from django.db.models.functions import Lower

            alarms = (
                AlarmConfig.objects.all()
                .select_related("alarm_class")
                .annotate(alarm_class_display=Lower("alarm_class__verbose_name_ru"))
                .order_by("alarm_class_display", "prior", "table__name")
            )

            # Формируем структуру данных для экспорта
            export_data = {"alarm_tables": [], "alarm_configs": []}

            # Добавляем таблицы тревог
            tables = AlarmTable.objects.all()
            for table in tables:
                export_data["alarm_tables"].append(
                    {
                        "id": table.id,
                        "name": table.name,
                        "description": table.description,
                        "created_at": table.created_at.isoformat(),
                        "updated_at": table.updated_at.isoformat(),
                    }
                )

            # Добавляем конфигурации аварий
            for alarm in alarms:
                alarm_data = {
                    "id": alarm.id,
                    "alarm_class": (
                        alarm.alarm_class.verbose_name_ru if alarm.alarm_class else None
                    ),
                    "table_id": alarm.table.id,
                    "logic": alarm.logic.verbose_name_ru if alarm.logic else None,
                    "channel": alarm.channel,
                    "limit_type": (
                        alarm.limit_type.verbose_name_ru if alarm.limit_type else None
                    ),
                    "limit_config_type": (
                        alarm.limit_config_type.verbose_name_ru
                        if alarm.limit_config_type
                        else None
                    ),
                    "low": alarm.low,
                    "high": alarm.high,
                    "discrete_val": alarm.discrete_val,
                    "msg": alarm.msg,
                    "hyst_low": alarm.hyst_low,
                    "hyst_high": alarm.hyst_high,
                    "ch_low": alarm.ch_low,
                    "ch_high": alarm.ch_high,
                    "confirm_method": (
                        alarm.confirm_method.verbose_name_ru
                        if alarm.confirm_method
                        else None
                    ),
                    "prior": alarm.prior,
                    "created_at": alarm.created_at.isoformat(),
                    "updated_at": alarm.updated_at.isoformat(),
                }
                export_data["alarm_configs"].append(alarm_data)

            # Создаем JSON ответ
            response = HttpResponse(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )
            response["Content-Disposition"] = 'attachment; filename="alarm_config.json"'
            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


@csrf_exempt
def get_logic_fields(request):
    """AJAX запрос для получения полей в зависимости от выбранной логики"""
    if request.method == "POST":
        logic = request.POST.get("logic")

        # Определяем какие поля нужно показать/скрыть
        fields_config = {
            "discrete": {
                "show": ["channel", "discrete_val", "msg", "confirm_method", "prior"],
                "hide": [
                    "limit_type",
                    "limit_config_type",
                    "low",
                    "high",
                    "hyst_low",
                    "hyst_high",
                    "ch_low",
                    "ch_high",
                ],
            },
            "analog": {
                "show": [
                    "channel",
                    "limit_type",
                    "limit_config_type",
                    "low",
                    "high",
                    "msg",
                    "hyst_low",
                    "hyst_high",
                    "ch_low",
                    "ch_high",
                    "confirm_method",
                    "prior",
                ],
                "hide": ["discrete_val"],
            },
            "change": {
                "show": ["channel", "msg", "confirm_method", "prior"],
                "hide": [
                    "limit_type",
                    "limit_config_type",
                    "low",
                    "high",
                    "discrete_val",
                    "hyst_low",
                    "hyst_high",
                    "ch_low",
                    "ch_high",
                ],
            },
        }

        return JsonResponse(fields_config.get(logic, {"show": [], "hide": []}))

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


@require_GET
def api_alarm_classes(request):
    data = list(AlarmClass.objects.values("id", "verbose_name_ru"))
    return JsonResponse(data, safe=False)


@require_GET
def api_logics(request):
    data = list(Logic.objects.values("id", "verbose_name_ru"))
    return JsonResponse(data, safe=False)


@require_GET
def api_confirm_methods(request):
    data = list(ConfirmMethod.objects.values("id", "verbose_name_ru"))
    return JsonResponse(data, safe=False)


@require_GET
def api_limit_types(request):
    data = list(LimitType.objects.values("id", "verbose_name_ru"))
    return JsonResponse(data, safe=False)


@require_GET
def api_limit_config_types(request):
    data = list(LimitConfigType.objects.values("id", "verbose_name_ru"))
    return JsonResponse(data, safe=False)


@require_GET
def api_next_table_number(request):
    """API для получения следующего доступного номера таблицы"""
    next_number = AlarmTable.get_next_available_number()
    return JsonResponse({"next_number": next_number})


@require_GET
def api_used_table_numbers(request):
    """API для получения списка уже использованных номеров таблиц"""
    used_numbers = list(AlarmTable.objects.values_list("table_number", flat=True))
    return JsonResponse({"used_numbers": used_numbers})
