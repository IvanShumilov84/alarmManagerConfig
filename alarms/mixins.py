class FilterMixin:
    """Миксин для унифицированной фильтрации"""

    def apply_filters(self, queryset):
        """Применяет фильтры к queryset"""
        # Получаем параметры фильтрации из GET запроса
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
            filter_operator = self.request.GET.get(f"filter_op_{i}", "contains")
            filter_operators.append(filter_operator)
            i += 1

        # Применяем фильтры
        for i, field in enumerate(filter_fields):
            if i < len(filter_values) and filter_values[i].strip():
                value = filter_values[i].strip()
                operator = (
                    filter_operators[i] if i < len(filter_operators) else "contains"
                )

                # Применяем фильтр в зависимости от поля
                queryset = self._apply_single_filter(
                    queryset, field, operator, value, i
                )

        return queryset

    def _apply_single_filter(self, queryset, field, operator, value, index):
        """Применяет один фильтр к queryset"""

        # Фильтрация по ID
        if field == "id":
            return self._filter_by_id(queryset, operator, value)

        # Фильтрация по текстовым полям
        elif field in ["name", "description", "alarm_class", "logic", "channel", "msg"]:
            return self._filter_by_text_field(queryset, field, operator, value)

        # Фильтрация по числовым полям
        elif field in ["alarms_count", "prior"]:
            return self._filter_by_number_field(queryset, field, operator, value)

        # Фильтрация по датам
        elif field in ["created_at", "updated_at", "deleted_at"]:
            return self._filter_by_date_field(queryset, field, operator, value, index)

        # Фильтрация по связанным полям
        elif field == "table":
            return self._filter_by_related_field(queryset, field, operator, value)

        return queryset

    def _filter_by_id(self, queryset, operator, value):
        """Фильтрация по ID"""
        try:
            int_value = int(value)
            if operator == "exact":
                return queryset.filter(id=int_value)
            elif operator == "contains":
                return queryset.filter(id__icontains=int_value)
            elif operator == "startswith":
                return queryset.filter(id__istartswith=int_value)
            elif operator == "endswith":
                return queryset.filter(id__iendswith=int_value)
            elif operator == "gt":
                return queryset.filter(id__gt=int_value)
            elif operator == "lt":
                return queryset.filter(id__lt=int_value)
            elif operator == "gte":
                return queryset.filter(id__gte=int_value)
            elif operator == "lte":
                return queryset.filter(id__lte=int_value)
        except ValueError:
            return queryset.none()
        return queryset

    def _filter_by_text_field(self, queryset, field, operator, value):
        """Фильтрация по текстовым полям"""
        # Специальная обработка для alarm_class
        if field == "alarm_class":
            return self._filter_by_alarm_class(queryset, operator, value)
        # Специальная обработка для logic
        elif field == "logic":
            return self._filter_by_logic(queryset, operator, value)
        # Обычная обработка для остальных текстовых полей
        else:
            if operator == "exact":
                return queryset.filter(**{f"{field}__iexact": value})
            elif operator == "contains":
                return queryset.filter(**{f"{field}__iregex": value})
            elif operator == "startswith":
                return queryset.filter(**{f"{field}__iregex": f"^{value}"})
            elif operator == "endswith":
                return queryset.filter(**{f"{field}__iregex": f"{value}$"})
        return queryset

    def _filter_by_alarm_class(self, queryset, operator, value):
        """Фильтрация по полю alarm_class с поддержкой русских названий"""
        search_value = value.lower()

        # Для точного поиска ищем точное совпадение
        if operator == "exact":
            return queryset.filter(alarm_class__verbose_name_ru__iexact=value)
        elif operator == "contains":
            # Для поиска "содержит" ищем частичные совпадения
            return queryset.filter(alarm_class__verbose_name_ru__icontains=value)
        elif operator == "startswith":
            # Для поиска "начинается с" ищем значения, начинающиеся с поискового запроса
            return queryset.filter(alarm_class__verbose_name_ru__istartswith=value)
        elif operator == "endswith":
            # Для поиска "заканчивается на" ищем значения, заканчивающиеся на поисковый запрос
            return queryset.filter(alarm_class__verbose_name_ru__iendswith=value)
        return queryset

    def _filter_by_logic(self, queryset, operator, value):
        """Фильтрация по полю logic с поддержкой русских названий"""
        # Для точного поиска ищем точное совпадение
        if operator == "exact":
            return queryset.filter(logic__verbose_name_ru__iexact=value)
        elif operator == "contains":
            # Для поиска "содержит" ищем частичные совпадения
            return queryset.filter(logic__verbose_name_ru__icontains=value)
        elif operator == "startswith":
            # Для поиска "начинается с" ищем значения, начинающиеся с поискового запроса
            return queryset.filter(logic__verbose_name_ru__istartswith=value)
        elif operator == "endswith":
            # Для поиска "заканчивается на" ищем значения, заканчивающиеся на поисковый запрос
            return queryset.filter(logic__verbose_name_ru__iendswith=value)
        return queryset

    def _filter_by_number_field(self, queryset, field, operator, value):
        """Фильтрация по числовым полям"""
        try:
            int_value = int(value)
            if operator == "exact":
                return queryset.filter(**{field: int_value})
            elif operator == "gt":
                return queryset.filter(**{f"{field}__gt": int_value})
            elif operator == "lt":
                return queryset.filter(**{f"{field}__lt": int_value})
            elif operator == "gte":
                return queryset.filter(**{f"{field}__gte": int_value})
            elif operator == "lte":
                return queryset.filter(**{f"{field}__lte": int_value})
        except ValueError:
            return queryset.none()
        return queryset

    def _filter_by_date_field(self, queryset, field, operator, value, index):
        """Фильтрация по полям дат с учетом локальной даты (как в фильтре exact)"""
        if operator == "exact":
            return queryset.filter(**{f"{field}__date": value})
        elif operator == "gt":
            return queryset.filter(**{f"{field}__date__gt": value})
        elif operator == "lt":
            return queryset.filter(**{f"{field}__date__lt": value})
        elif operator == "gte":
            return queryset.filter(**{f"{field}__date__gte": value})
        elif operator == "lte":
            return queryset.filter(**{f"{field}__date__lte": value})
        elif operator == "range":
            start_value = self.request.GET.get(f"filter_value_{index}_start")
            end_value = self.request.GET.get(f"filter_value_{index}_end")
            if start_value:
                queryset = queryset.filter(**{f"{field}__date__gte": start_value})
            if end_value:
                queryset = queryset.filter(**{f"{field}__date__lte": end_value})
        return queryset

    def _filter_by_related_field(self, queryset, field, operator, value):
        """Фильтрация по связанным полям"""
        if field == "table":
            if operator == "exact":
                return queryset.filter(table__name__iexact=value)
            elif operator == "contains":
                return queryset.filter(table__name__iregex=value)
            elif operator == "startswith":
                return queryset.filter(table__name__iregex=f"^{value}")
            elif operator == "endswith":
                return queryset.filter(table__name__iregex=f"{value}$")
        return queryset
