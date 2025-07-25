from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy
import json
from .models import AlarmConfig, AlarmTable
from .forms import AlarmConfigForm, AlarmTableForm
from django.http import HttpResponseRedirect
from .mixins import FilterMixin
from .models import AlarmClass, Logic, ConfirmMethod, LimitType, LimitConfigType
from django.views.decorators.http import require_GET


class AlarmTableListView(FilterMixin, ListView):
    """Представление для списка таблиц аварий"""

    model = AlarmTable
    template_name = "alarms/table_list.html"
    context_object_name = "tables"
    paginate_by = 20

    def get_queryset(self):
        """Получаем queryset с подсчетом тревог для каждой таблицы и применяем фильтры"""
        from django.db.models import Count

        queryset = AlarmTable.objects.all().annotate(alarms_count=Count("alarms"))

        # Применяем фильтрацию через миксин
        queryset = self.apply_filters(queryset)

        # Применяем сортировку
        sort_fields = []
        sort_orders = []

        # Собираем все параметры сортировки с индексами
        i = 0
        while True:
            sort_field = self.request.GET.get(f"sort_{i}")
            if not sort_field:
                break
            sort_fields.append(sort_field)
            sort_order = self.request.GET.get(f"order_{i}", "asc")
            sort_orders.append(sort_order)
            i += 1

        # Применяем сортировку
        if sort_fields:
            order_by_fields = []
            for i, field in enumerate(sort_fields):
                if field:
                    order = sort_orders[i] if i < len(sort_orders) else "asc"
                    if order == "desc":
                        order_by_fields.append(f"-{field}")
                    else:
                        order_by_fields.append(field)

            if order_by_fields:
                queryset = queryset.order_by(*order_by_fields)
        else:
            # Сортировка по умолчанию
            queryset = queryset.order_by("table_number")

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем базовые параметры в контекст"""
        context = super().get_context_data(**kwargs)

        # Добавляем счетчики для отображения в бейджах
        total_count = AlarmTable.objects.all().count()

        # Новый способ определения наличия активных фильтров
        has_active_filters = any(
            key.startswith("filter_field_") for key in self.request.GET.keys()
        )
        # Если есть активные фильтры, подсчитываем отфильтрованные записи
        if has_active_filters:
            # Получаем queryset без пагинации для подсчета всех отфильтрованных записей
            from django.db.models import Count

            filtered_queryset = AlarmTable.objects.all().annotate(
                alarms_count=Count("alarms")
            )
            filtered_queryset = self.apply_filters(filtered_queryset)
            filtered_count = filtered_queryset.count()
        else:
            filtered_count = total_count

        context["total_count"] = total_count
        context["filtered_count"] = filtered_count
        context["has_active_filters"] = has_active_filters

        # Добавляем поля сортировки для таблиц
        context["sort_fields"] = get_sort_fields("tables")
        context["storage_key"] = "tablesSortFields"

        # Добавляем поля фильтров для таблиц
        context["filter_fields"] = get_filter_fields("tables")

        # Получаем параметры сортировки
        sort_fields = []
        sort_orders = []

        # Собираем все параметры сортировки с индексами
        i = 0
        while True:
            sort_field = self.request.GET.get(f"sort_{i}")
            if not sort_field:
                break
            sort_fields.append(sort_field)
            sort_order = self.request.GET.get(f"order_{i}", "asc")
            sort_orders.append(sort_order)
            i += 1

        # Для обратной совместимости
        context["sort_orders"] = sort_orders[: len(sort_fields)]

        # Создаем словарь для отображения стрелок в заголовках таблицы
        context["sort_indicators"] = {}
        for i, field in enumerate(sort_fields):
            if field and i < len(sort_orders):
                context["sort_indicators"][field] = sort_orders[i]

        context["current_sort"] = self.request.GET.get("sort", "table_number")
        context["current_order"] = self.request.GET.get("order", "asc")

        # Добавляем display_mode для controls_panel
        context["display_mode"] = "tables"

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


class AlarmConfigListView(FilterMixin, ListView):
    """Представление для списка конфигураций аварий"""

    model = AlarmConfig
    template_name = "alarms/alarm_list.html"
    context_object_name = "alarms"
    paginate_by = 20

    def get_queryset(self):
        """Получаем queryset с поддержкой сортировки и фильтрации по русским названиям"""
        from django.db.models.functions import Lower

        queryset = AlarmConfig.objects.all().select_related(
            "table", "alarm_class", "logic", "limit_type", "confirm_method"
        )

        # Применяем фильтрацию через миксин
        queryset = self.apply_filters(queryset)

        # Получаем параметры сортировки
        sort_fields = []
        sort_orders = []

        # Собираем все параметры сортировки с индексами
        i = 0
        while True:
            sort_field = self.request.GET.get(f"sort_{i}")
            if not sort_field:
                break
            sort_fields.append(sort_field)
            sort_order = self.request.GET.get(f"order_{i}", "asc")
            sort_orders.append(sort_order)
            i += 1

        # Если нет параметров сортировки, используем значения по умолчанию
        if not sort_fields:
            sort_fields = ["id"]
            sort_orders = ["asc"]

        # Создаем аннотации для сортировки по русским названиям
        queryset = queryset.annotate(
            alarm_class_display=Lower("alarm_class__verbose_name_ru"),
            logic_display=Lower("logic__verbose_name_ru"),
            limit_type_display=Lower("limit_type__verbose_name_ru"),
            limit_config_type_display=Lower("limit_config_type__verbose_name_ru"),
            confirm_method_display=Lower("confirm_method__verbose_name_ru"),
            channel_lower=Lower("channel"),
        )

        # Список разрешенных полей для сортировки с русскими названиями
        allowed_fields = {
            "id": "id",
            "alarm_class": "alarm_class_display",
            "table": "table__name",
            "logic": "logic_display",
            "channel": "channel_lower",
            "msg": "msg",
            "prior": "prior",
            "limit_type": "limit_type_display",
            "limit_config_type": "limit_config_type_display",
            "confirm_method": "confirm_method_display",
            "low": "low",
            "high": "high",
            "ch_low": "ch_low",
            "ch_high": "ch_high",
            "hyst_low": "hyst_low",
            "hyst_high": "hyst_high",
            "discrete_val": "discrete_val",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Определяем вторичные поля для групповой сортировки
        secondary_sort_fields = {
            "alarm_class": ["id"],
            "table": ["id"],
            "logic": ["id"],
            "channel": ["id"],
            "msg": ["id"],
            "prior": ["id"],
            "limit_type": ["id"],
            "limit_config_type": ["id"],
            "confirm_method": ["id"],
            "low": ["id"],
            "high": ["id"],
            "ch_low": ["id"],
            "ch_high": ["id"],
            "hyst_low": ["id"],
            "hyst_high": ["id"],
            "discrete_val": ["id"],
            "created_at": ["id"],
            "updated_at": ["id"],
        }

        # Создаем список полей для сортировки
        order_fields = []
        used_fields = set()  # Множество уже использованных полей

        # Сначала добавляем все основные поля сортировки пользователя
        for i, field in enumerate(sort_fields):
            if field in allowed_fields:
                db_field = allowed_fields[field]
                order = sort_orders[i] if i < len(sort_orders) else "asc"
                order_field = f"{'-' if order == 'desc' else ''}{db_field}"
                order_fields.append(order_field)
                used_fields.add(db_field)  # Добавляем поле без знака минус

        # Затем добавляем вторичные поля, но только если они не совпадают
        for i, field in enumerate(sort_fields):
            if field in allowed_fields and field in secondary_sort_fields:
                for secondary_field in secondary_sort_fields[field]:
                    # Добавляем вторичное поле только если оно не совпадает
                    if secondary_field not in used_fields:
                        order_fields.append(secondary_field)
                        used_fields.add(secondary_field)

        # Применяем сортировку
        if order_fields:
            queryset = queryset.order_by(*order_fields)

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем параметры сортировки в контекст"""
        context = super().get_context_data(**kwargs)

        # Получаем параметры сортировки
        sort_fields = []
        sort_orders = []

        # Собираем все параметры сортировки с индексами
        i = 0
        while True:
            sort_field = self.request.GET.get(f"sort_{i}")
            if not sort_field:
                break
            sort_fields.append(sort_field)
            sort_order = self.request.GET.get(f"order_{i}", "asc")
            sort_orders.append(sort_order)
            i += 1

        # Добавляем поля сортировки для тревог
        context["sort_fields"] = get_sort_fields("alarms")
        context["storage_key"] = "alarmsSortFields"

        # Добавляем поля фильтров для тревог
        context["filter_config"] = get_filter_fields("alarms")

        # Для обратной совместимости
        context["sort_orders"] = sort_orders[: len(sort_fields)]

        # Создаем словарь для отображения стрелок в заголовках таблицы
        context["sort_indicators"] = {}
        for i, field in enumerate(sort_fields):
            if field and i < len(sort_orders):
                context["sort_indicators"][field] = sort_orders[i]

        context["current_sort"] = self.request.GET.get("sort", "alarm_class")
        context["current_order"] = self.request.GET.get("order", "asc")

        # Добавляем параметры фильтров в контекст для ссылок пагинации
        filter_fields = []
        filter_ops = []
        filter_values = []

        # Собираем все параметры фильтров с индексами
        i = 0
        while True:
            filter_field = self.request.GET.get(f"filter_field_{i}")
            if not filter_field:
                break
            filter_fields.append(filter_field)
            filter_op = self.request.GET.get(f"filter_op_{i}", "exact")
            filter_ops.append(filter_op)
            filter_value = self.request.GET.get(f"filter_value_{i}", "")
            filter_values.append(filter_value)
            i += 1

        context["filter_fields"] = filter_fields
        context["filter_ops"] = filter_ops
        context["filter_values"] = filter_values

        # Получаем отфильтрованный queryset для подсчета
        filtered_queryset = AlarmConfig.objects.all()
        filtered_queryset = self.apply_filters(filtered_queryset)
        context["filtered_count"] = filtered_queryset.count()

        # Проверяем, есть ли активные фильтры
        has_active_filters = any(
            field and value and value.strip()
            for field, value in zip(filter_fields, filter_values)
        )
        context["has_active_filters"] = has_active_filters

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
    """API для получения списка занятых номеров таблиц"""
    # Получаем все занятые номера таблиц, исключая текущую редактируемую таблицу
    current_table_id = request.GET.get("exclude_id")

    if current_table_id:
        used_numbers = list(
            AlarmTable.objects.exclude(id=current_table_id).values_list(
                "table_number", flat=True
            )
        )
    else:
        used_numbers = list(AlarmTable.objects.values_list("table_number", flat=True))

    return JsonResponse(
        {"used_numbers": sorted(used_numbers), "count": len(used_numbers)}
    )


# Единая конфигурация полей для фильтров и сортировки
FIELDS_CONFIG = {
    "tables": [
        # {"value": "id", "label": "ID", "type": "number"},
        {
            "value": "table_number",
            "label": "Номер таблицы",
            "short_label": "Номер",
            "type": "number",
        },
        {
            "value": "name",
            "label": "Название",
            "short_label": "Название",
            "type": "text",
        },
        {
            "value": "description",
            "label": "Описание",
            "short_label": "Описание",
            "type": "text",
        },
        {
            "value": "alarms_count",
            "label": "Количество тревог",
            "short_label": "Кол-во",
            "type": "number",
        },
        {
            "value": "created_at",
            "label": "Дата создания",
            "short_label": "Создано",
            "type": "date",
        },
        {
            "value": "updated_at",
            "label": "Дата обновления",
            "short_label": "Обновлено",
            "type": "date",
        },
    ],
    "alarms": [
        {"value": "id", "label": "ID", "short_label": "ID", "type": "number"},
        {
            "value": "alarm_class",
            "label": "Класс тревоги",
            "short_label": "Класс",
            "type": "select",
        },
        {
            "value": "table",
            "label": "Таблица",
            "short_label": "Таблица",
            "type": "select",
        },
        {
            "value": "logic",
            "label": "Способ наблюдения",
            "short_label": "Логика",
            "type": "select",
        },
        {"value": "channel", "label": "Канал", "short_label": "Канал", "type": "text"},
        {
            "value": "msg",
            "label": "Сообщение",
            "short_label": "Сообщение",
            "type": "text",
        },
        {
            "value": "prior",
            "label": "Приоритет",
            "short_label": "Приоритет",
            "type": "number",
        },
        {
            "value": "confirm_method",
            "label": "Способ подтверждения",
            "short_label": "Подтверждение",
            "type": "select",
        },
        {
            "value": "limit_type",
            "label": "Тип ограничения",
            "short_label": "Лимит",
            "type": "select",
        },
        {
            "value": "limit_config_type",
            "label": "Тип настройки пределов",
            "short_label": "Тип лимита",
            "type": "select",
        },
        {
            "value": "low",
            "label": "Нижний предел",
            "short_label": "Мин",
            "type": "number",
        },
        {
            "value": "high",
            "label": "Верхний предел",
            "short_label": "Макс",
            "type": "number",
        },
        {
            "value": "hyst_low",
            "label": "Гистерезис нижнего предела",
            "short_label": "Гист мин",
            "type": "number",
        },
        {
            "value": "hyst_high",
            "label": "Гистерезис верхнего предела",
            "short_label": "Гист макс",
            "type": "number",
        },
        {
            "value": "ch_low",
            "label": "Канал нижнего предела",
            "short_label": "Канал мин",
            "type": "text",
        },
        {
            "value": "ch_high",
            "label": "Канал верхнего предела",
            "short_label": "Канал макс",
            "type": "text",
        },
        {
            "value": "discrete_val",
            "label": "Значение предела для дискретного сигнала",
            "short_label": "Дискрет",
            "type": "number",
        },
        {
            "value": "created_at",
            "label": "Дата создания",
            "short_label": "Создано",
            "type": "date",
        },
        {
            "value": "updated_at",
            "label": "Дата обновления",
            "short_label": "Обновлено",
            "type": "date",
        },
    ],
}


def get_filter_fields(page_type):
    """Возвращает поля для фильтров с типами"""
    return FIELDS_CONFIG.get(page_type, [])


def get_sort_fields(page_type):
    """Возвращает поля для сортировки без типов"""
    fields = FIELDS_CONFIG.get(page_type, [])
    return [
        {"value": f["value"], "label": f["label"], "short_label": f["short_label"]}
        for f in fields
    ]


@require_GET
def api_filter_fields(request):
    """API для получения списка полей фильтров"""
    page_type = request.GET.get("type", "tables")  # tables или alarms

    if page_type not in FIELDS_CONFIG:
        return JsonResponse({"error": "Неизвестный тип страницы"}, status=400)

    fields = get_filter_fields(page_type)
    return JsonResponse({"fields": fields, "type": page_type})


@require_GET
def api_sort_fields(request):
    """API для получения списка полей сортировки"""
    page_type = request.GET.get("type", "tables")  # tables или alarms

    if page_type not in FIELDS_CONFIG:
        return JsonResponse({"error": "Неизвестный тип страницы"}, status=400)

    fields = get_sort_fields(page_type)
    return JsonResponse({"fields": fields, "type": page_type})


def ajax_sort_alarms(request):
    """AJAX endpoint для сортировки тревог без перезагрузки страницы"""
    from django.template.loader import render_to_string
    from django.db.models.functions import Lower
    from django.core.paginator import Paginator

    # Получаем queryset с фильтрами и сортировкой
    queryset = AlarmConfig.objects.all().select_related(
        "table", "alarm_class", "logic", "limit_type", "confirm_method"
    )

    # Применяем фильтрацию через миксин
    filter_mixin = FilterMixin()
    filter_mixin.request = request
    queryset = filter_mixin.apply_filters(queryset)

    # Получаем параметры сортировки
    sort_fields = []
    sort_orders = []

    # Собираем все параметры сортировки с индексами
    i = 0
    while True:
        sort_field = request.GET.get(f"sort_{i}")
        if not sort_field:
            break
        sort_fields.append(sort_field)
        sort_order = request.GET.get(f"order_{i}", "asc")
        sort_orders.append(sort_order)
        i += 1

    # Если нет параметров сортировки, используем значения по умолчанию
    if not sort_fields:
        sort_fields = ["id"]
        sort_orders = ["asc"]

    # Создаем аннотации для сортировки по русским названиям
    queryset = queryset.annotate(
        alarm_class_display=Lower("alarm_class__verbose_name_ru"),
        logic_display=Lower("logic__verbose_name_ru"),
        limit_type_display=Lower("limit_type__verbose_name_ru"),
        limit_config_type_display=Lower("limit_config_type__verbose_name_ru"),
        confirm_method_display=Lower("confirm_method__verbose_name_ru"),
        channel_lower=Lower("channel"),
    )

    # Список разрешенных полей для сортировки с русскими названиями
    allowed_fields = {
        "id": "id",
        "alarm_class": "alarm_class_display",
        "table": "table__name",
        "logic": "logic_display",
        "channel": "channel_lower",
        "msg": "msg",
        "prior": "prior",
        "limit_type": "limit_type_display",
        "limit_config_type": "limit_config_type_display",
        "confirm_method": "confirm_method_display",
        "low": "low",
        "high": "high",
        "ch_low": "ch_low",
        "ch_high": "ch_high",
        "hyst_low": "hyst_low",
        "hyst_high": "hyst_high",
        "discrete_val": "discrete_val",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }

    # Определяем вторичные поля для групповой сортировки
    secondary_sort_fields = {
        "alarm_class": ["id"],
        "table": ["id"],
        "logic": ["id"],
        "channel": ["id"],
        "msg": ["id"],
        "prior": ["id"],
        "limit_type": ["id"],
        "limit_config_type": ["id"],
        "confirm_method": ["id"],
        "low": ["id"],
        "high": ["id"],
        "ch_low": ["id"],
        "ch_high": ["id"],
        "hyst_low": ["id"],
        "hyst_high": ["id"],
        "discrete_val": ["id"],
        "created_at": ["id"],
        "updated_at": ["id"],
    }

    # Создаем список полей для сортировки
    order_fields = []
    used_fields = set()

    # Сначала добавляем все основные поля сортировки пользователя
    for i, field in enumerate(sort_fields):
        if field in allowed_fields:
            db_field = allowed_fields[field]
            order = sort_orders[i] if i < len(sort_orders) else "asc"
            order_field = f"{'-' if order == 'desc' else ''}{db_field}"
            order_fields.append(order_field)
            used_fields.add(db_field)

    # Затем добавляем вторичные поля, но только если они не совпадают
    for i, field in enumerate(sort_fields):
        if field in allowed_fields and field in secondary_sort_fields:
            for secondary_field in secondary_sort_fields[field]:
                if secondary_field not in used_fields:
                    order_fields.append(secondary_field)
                    used_fields.add(secondary_field)

    # Применяем сортировку
    if order_fields:
        queryset = queryset.order_by(*order_fields)

    # Применяем пагинацию
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Рендерим реальные шаблоны с данными
    table_html = render_to_string(
        "alarms/includes/alarm_table_rows.html",
        {
            "alarms": page_obj,
            "page_obj": page_obj,
        },
    )

    # Рендерим пагинацию
    pagination_html = render_to_string(
        "alarms/includes/pagination.html",
        {
            "page_obj": page_obj,
        },
    )

    response = JsonResponse(
        {
            "success": True,
            "message": f"AJAX сортировка завершена! Загружено {len(page_obj)} из {paginator.count} записей",
            "table_html": table_html,
            "pagination_html": pagination_html,
            "total_count": paginator.count,
            "current_page": page_obj.number,
            "num_pages": paginator.num_pages,
            "sort_fields": sort_fields,
            "sort_orders": sort_orders,
        }
    )

    # Добавляем CORS заголовки для разработки
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"

    return response
