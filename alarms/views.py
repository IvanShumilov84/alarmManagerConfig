from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json
from .models import AlarmConfig, AlarmTable
from .forms import AlarmConfigForm, AlarmTableForm


class AlarmTableListView(ListView):
    """Представление для списка таблиц аварий"""

    model = AlarmTable
    template_name = "alarms/table_list.html"
    context_object_name = "tables"
    paginate_by = 20

    def get_queryset(self):
        """Получаем queryset с поддержкой множественной сортировки"""
        from django.db.models import Count

        queryset = AlarmTable.objects.annotate(alarms_count=Count("alarms"))

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
            sort_fields = ["name"]
            sort_orders = ["asc"]

        # Список разрешенных полей для сортировки
        allowed_fields = {
            "id": "id",
            "name": "name",
            "description": "description",
            "alarms_count": "alarms_count",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Создаем список полей для сортировки
        order_fields = []

        # Обрабатываем каждое поле сортировки
        for i, sort_field in enumerate(sort_fields):
            if sort_field in allowed_fields:
                field_name = allowed_fields[sort_field]
                # Получаем порядок для этого поля (по умолчанию asc)
                order = sort_orders[i] if i < len(sort_orders) else "asc"
                if order == "desc":
                    field_name = f"-{field_name}"
                order_fields.append(field_name)

        # Применяем сортировку
        if order_fields:
            queryset = queryset.order_by(*order_fields)
        else:
            # По умолчанию сортируем по названию
            queryset = queryset.order_by("name")

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

        # Для обратной совместимости
        context["sort_fields"] = [field for field in sort_fields if field]
        context["sort_orders"] = sort_orders[: len(context["sort_fields"])]

        # Создаем словарь для отображения стрелок в заголовках таблицы
        context["sort_indicators"] = {}
        for i, field in enumerate(sort_fields):
            if field and i < len(sort_orders):
                context["sort_indicators"][field] = sort_orders[i]

        return context


class AlarmTableCreateView(CreateView):
    """Представление для создания новой таблицы аварий"""

    model = AlarmTable
    form_class = AlarmTableForm
    template_name = "alarms/table_form.html"
    success_url = reverse_lazy("alarms:table_list")


class AlarmTableUpdateView(UpdateView):
    """Представление для редактирования таблицы аварий"""

    model = AlarmTable
    form_class = AlarmTableForm
    template_name = "alarms/table_form.html"
    success_url = reverse_lazy("alarms:table_list")


class AlarmTableDeleteView(DeleteView):
    """Представление для удаления таблицы аварий"""

    model = AlarmTable
    template_name = "alarms/table_confirm_delete.html"
    success_url = reverse_lazy("alarms:table_list")


class AlarmConfigListView(ListView):
    """Представление для списка конфигураций аварий"""

    model = AlarmConfig
    template_name = "alarms/alarm_list.html"
    context_object_name = "alarms"
    paginate_by = 20

    def get_queryset(self):
        """Получаем queryset с поддержкой сортировки и фильтрации по русским названиям"""
        from django.db.models import Case, When, Value, CharField, Q

        queryset = AlarmConfig.objects.select_related("table")

        # Применяем фильтрацию
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
            sort_fields = ["alarm_class"]
            sort_orders = ["asc"]

        # Создаем аннотации для сортировки по русским названиям
        from django.db.models.functions import Lower

        queryset = queryset.annotate(
            alarm_class_display=Case(
                When(alarm_class="error", then=Value("Ошибка")),
                When(alarm_class="warn", then=Value("Предупреждение")),
                When(alarm_class="info", then=Value("Информирование")),
                default=Value(""),
                output_field=CharField(),
            ),
            logic_display=Case(
                When(logic="discrete", then=Value("Дискретное событие")),
                When(logic="analog", then=Value("Аналоговое событие")),
                When(logic="change", then=Value("Изменение события")),
                default=Value(""),
                output_field=CharField(),
            ),
            limit_type_display=Case(
                When(limit_type="low", then=Value("Ограничение снизу")),
                When(limit_type="high", then=Value("Ограничение сверху")),
                When(limit_type="low_high", then=Value("Ограничение снизу и сверху")),
                default=Value(""),
                output_field=CharField(),
            ),
            confirm_method_display=Case(
                When(
                    confirm_method="rep_ack",
                    then=Value("Квитирование деактивированной тревоги"),
                ),
                default=Value(""),
                output_field=CharField(),
            ),
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
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Определяем вторичные поля для групповой сортировки
        secondary_sort_fields = {
            "id": ["alarm_class_display", "prior"],
            "alarm_class": ["prior", "table__name"],
            "table": ["alarm_class_display", "prior"],
            "logic": ["alarm_class_display", "prior"],
            "channel": ["alarm_class_display", "prior"],
            "msg": ["alarm_class_display", "prior"],
            "prior": ["alarm_class_display", "table__name"],
            "created_at": ["alarm_class_display", "prior"],
            "updated_at": ["alarm_class_display", "prior"],
        }

        # Создаем список полей для сортировки
        order_fields = []

        # Обрабатываем каждое поле сортировки
        for i, sort_field in enumerate(sort_fields):
            if sort_field in allowed_fields:
                field_name = allowed_fields[sort_field]
                # Получаем порядок для этого поля (по умолчанию asc)
                order = sort_orders[i] if i < len(sort_orders) else "asc"
                if order == "desc":
                    field_name = f"-{field_name}"
                order_fields.append(field_name)

        # Применяем сортировку
        if order_fields:
            queryset = queryset.order_by(*order_fields)
        else:
            # По умолчанию сортируем по русским названиям класса и приоритету
            queryset = queryset.order_by("alarm_class_display", "prior")

        return queryset

    def apply_filters(self, queryset):
        """Применяет фильтры к queryset"""
        from django.db.models import Q

        # Получаем параметры фильтрации
        filter_fields = []
        filter_values = []
        filter_operators = []

        # Собираем все параметры фильтрации с индексами
        i = 0
        while True:
            filter_field = self.request.GET.get(f"filter_field_{i}")
            if not filter_field:
                break
            filter_fields.append(filter_field)
            filter_value = self.request.GET.get(f"filter_value_{i}", "")
            filter_values.append(filter_value)
            filter_operator = self.request.GET.get(f"filter_operator_{i}", "contains")
            filter_operators.append(filter_operator)
            i += 1

        # Применяем фильтры
        for i, field in enumerate(filter_fields):
            if i < len(filter_values) and filter_values[i].strip():
                value = filter_values[i].strip()
                operator = (
                    filter_operators[i] if i < len(filter_operators) else "contains"
                )

                if field == "id":
                    try:
                        int_value = int(value)
                        if operator == "exact":
                            queryset = queryset.filter(id=int_value)
                        elif operator == "gt":
                            queryset = queryset.filter(id__gt=int_value)
                        elif operator == "lt":
                            queryset = queryset.filter(id__lt=int_value)
                        elif operator == "gte":
                            queryset = queryset.filter(id__gte=int_value)
                        elif operator == "lte":
                            queryset = queryset.filter(id__lte=int_value)
                    except ValueError:
                        # Если значение не является числом, возвращаем пустой queryset
                        return queryset.none()

                elif field == "alarm_class":
                    # Преобразуем русские названия в английские значения
                    alarm_class_mapping = {
                        "ошибка": "error",
                        "предупреждение": "warn",
                        "информирование": "info",
                        "error": "error",
                        "warn": "warn",
                        "info": "info",
                    }
                    search_value = value.lower()
                    if search_value in alarm_class_mapping:
                        db_value = alarm_class_mapping[search_value]
                        if operator == "exact":
                            queryset = queryset.filter(alarm_class=db_value)
                        elif operator == "contains":
                            queryset = queryset.filter(alarm_class=db_value)
                    else:
                        # Если не найдено точное соответствие
                        if operator == "exact":
                            # Для точного поиска возвращаем пустой queryset
                            return queryset.none()
                        elif operator == "contains":
                            # Ищем по всем возможным значениям
                            q_objects = Q()
                            for rus_name, eng_value in alarm_class_mapping.items():
                                if (
                                    search_value in rus_name
                                    or search_value in eng_value
                                ):
                                    q_objects |= Q(alarm_class=eng_value)
                            if q_objects:
                                queryset = queryset.filter(q_objects)
                            else:
                                # Если ничего не найдено, возвращаем пустой queryset
                                return queryset.none()

                elif field == "table":
                    if operator == "exact":
                        queryset = queryset.filter(table__name=value)
                    elif operator == "contains":
                        queryset = queryset.filter(table__name__icontains=value)

                elif field == "logic":
                    # Преобразуем русские названия в английские значения
                    logic_mapping = {
                        "дискретное событие": "discrete",
                        "аналоговое событие": "analog",
                        "изменение события": "change",
                        "discrete": "discrete",
                        "analog": "analog",
                        "change": "change",
                    }
                    search_value = value.lower()
                    if search_value in logic_mapping:
                        db_value = logic_mapping[search_value]
                        if operator == "exact":
                            queryset = queryset.filter(logic=db_value)
                        elif operator == "contains":
                            queryset = queryset.filter(logic=db_value)
                    else:
                        # Если не найдено точное соответствие
                        if operator == "exact":
                            # Для точного поиска возвращаем пустой queryset
                            return queryset.none()
                        elif operator == "contains":
                            # Ищем по всем возможным значениям
                            q_objects = Q()
                            for rus_name, eng_value in logic_mapping.items():
                                if (
                                    search_value in rus_name
                                    or search_value in eng_value
                                ):
                                    q_objects |= Q(logic=eng_value)
                            if q_objects:
                                queryset = queryset.filter(q_objects)
                            else:
                                # Если ничего не найдено, возвращаем пустой queryset
                                return queryset.none()

                elif field == "channel":
                    if operator == "exact":
                        queryset = queryset.filter(channel=value)
                    elif operator == "contains":
                        queryset = queryset.filter(channel__icontains=value)

                elif field == "msg":
                    if operator == "exact":
                        queryset = queryset.filter(msg=value)
                    elif operator == "contains":
                        queryset = queryset.filter(msg__icontains=value)

                elif field == "prior":
                    try:
                        int_value = int(value)
                        if operator == "exact":
                            queryset = queryset.filter(prior=int_value)
                        elif operator == "gt":
                            queryset = queryset.filter(prior__gt=int_value)
                        elif operator == "lt":
                            queryset = queryset.filter(prior__lt=int_value)
                        elif operator == "gte":
                            queryset = queryset.filter(prior__gte=int_value)
                        elif operator == "lte":
                            queryset = queryset.filter(prior__lte=int_value)
                    except ValueError:
                        # Если значение не является числом, возвращаем пустой queryset
                        return queryset.none()

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем режим отображения и параметры сортировки в контекст"""
        context = super().get_context_data(**kwargs)
        context["display_mode"] = self.request.GET.get("display_mode", "compact")

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
        context["sort_fields"] = [field for field in sort_fields if field]
        context["sort_orders"] = sort_orders[: len(context["sort_fields"])]

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

        return context


class AlarmTableDetailView(ListView):
    """Представление для отображения аварий конкретной таблицы"""

    model = AlarmConfig
    template_name = "alarms/table_detail.html"
    context_object_name = "alarms"
    paginate_by = 20

    def get_queryset(self):
        """Получаем аварии только для конкретной таблицы с сортировкой по русским названиям"""
        from django.db.models import Case, When, Value, CharField
        from django.db.models.functions import Lower

        self.table = get_object_or_404(AlarmTable, pk=self.kwargs["table_id"])
        queryset = AlarmConfig.objects.filter(table=self.table)

        # Создаем аннотации для сортировки по русским названиям
        queryset = queryset.annotate(
            alarm_class_display=Case(
                When(alarm_class="error", then=Value("Ошибка")),
                When(alarm_class="warn", then=Value("Предупреждение")),
                When(alarm_class="info", then=Value("Информирование")),
                default=Value(""),
                output_field=CharField(),
            ),
            logic_display=Case(
                When(logic="discrete", then=Value("Дискретное событие")),
                When(logic="analog", then=Value("Аналоговое событие")),
                When(logic="change", then=Value("Изменение события")),
                default=Value(""),
                output_field=CharField(),
            ),
            channel_lower=Lower("channel"),
        )

        # Групповая сортировка: сначала по классу, затем по приоритету, затем по каналу
        return queryset.order_by("alarm_class_display", "prior", "channel_lower")

    def get_context_data(self, **kwargs):
        """Добавляем информацию о таблице и режим отображения в контекст"""
        context = super().get_context_data(**kwargs)
        context["table"] = self.table
        context["display_mode"] = self.request.GET.get("display_mode", "compact")
        return context


class AlarmConfigCreateView(CreateView):
    """Представление для создания новой конфигурации аварии"""

    model = AlarmConfig
    form_class = AlarmConfigForm
    template_name = "alarms/alarm_form.html"
    success_url = reverse_lazy("alarms:alarm_list")

    def form_valid(self, form):
        messages.success(self.request, "Аварийный сигнал успешно создан!")
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
        messages.success(self.request, "Аварийный сигнал успешно обновлен!")
        return super().form_valid(form)


class AlarmConfigDeleteView(DeleteView):
    """Представление для удаления конфигурации аварии"""

    model = AlarmConfig
    template_name = "alarms/alarm_confirm_delete.html"
    success_url = reverse_lazy("alarms:alarm_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Аварийный сигнал успешно удален!")
        return super().delete(request, *args, **kwargs)


def dashboard(request):
    """Главная страница приложения"""
    from django.db.models import Case, When, Value, CharField

    tables_count = AlarmTable.objects.count()
    alarms_count = AlarmConfig.objects.count()

    # Получаем последние аварии с групповой сортировкой
    recent_alarms = AlarmConfig.objects.annotate(
        alarm_class_display=Case(
            When(alarm_class="error", then=Value("Ошибка")),
            When(alarm_class="warn", then=Value("Предупреждение")),
            When(alarm_class="info", then=Value("Информирование")),
            default=Value(""),
            output_field=CharField(),
        )
    ).order_by("-created_at", "alarm_class_display", "prior")[:5]

    context = {
        "tables_count": tables_count,
        "alarms_count": alarms_count,
        "recent_alarms": recent_alarms,
    }
    return render(request, "alarms/dashboard.html", context)


@csrf_exempt
def export_json(request):
    """Экспорт конфигураций аварий в JSON файл"""
    if request.method == "POST":
        try:
            # Получаем все конфигурации аварий с сортировкой по русским названиям
            from django.db.models import Case, When, Value, CharField

            alarms = AlarmConfig.objects.annotate(
                alarm_class_display=Case(
                    When(alarm_class="error", then=Value("Ошибка")),
                    When(alarm_class="warn", then=Value("Предупреждение")),
                    When(alarm_class="info", then=Value("Информирование")),
                    default=Value(""),
                    output_field=CharField(),
                )
            ).order_by("alarm_class_display", "prior", "table__name")

            # Формируем структуру данных для экспорта
            export_data = {"alarm_tables": [], "alarm_configs": []}

            # Добавляем таблицы аварий
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
                    "alarm_class": alarm.alarm_class,
                    "table_id": alarm.table.id,
                    "logic": alarm.logic,
                    "channel": alarm.channel,
                    "limit_type": alarm.limit_type,
                    "limit_config_type": alarm.limit_config_type,
                    "low": alarm.low,
                    "high": alarm.high,
                    "discrete_val": alarm.discrete_val,
                    "msg": alarm.msg,
                    "hyst_low": alarm.hyst_low,
                    "hyst_high": alarm.hyst_high,
                    "ch_low": alarm.ch_low,
                    "ch_high": alarm.ch_high,
                    "confirm_method": alarm.confirm_method,
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
