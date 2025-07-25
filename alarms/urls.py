from django.urls import path
from . import views

app_name = "alarms"

urlpatterns = [
    # Главная страница
    path("", views.dashboard, name="dashboard"),
    # Таблицы тревог
    path("tables/", views.AlarmTableListView.as_view(), name="table_list"),
    path("tables/create/", views.AlarmTableCreateView.as_view(), name="table_create"),
    path(
        "tables/<int:pk>/edit/", views.AlarmTableUpdateView.as_view(), name="table_edit"
    ),
    path(
        "tables/<int:pk>/delete/",
        views.AlarmTableDeleteView.as_view(),
        name="table_delete",
    ),
    path(
        "tables/<int:table_id>/alarms/",
        views.AlarmTableDetailView.as_view(),
        name="table_detail",
    ),
    # Конфигурации аварий
    path("alarms/", views.AlarmConfigListView.as_view(), name="alarm_list"),
    path("alarms/create/", views.AlarmConfigCreateView.as_view(), name="alarm_create"),
    path(
        "alarms/<int:pk>/edit/",
        views.AlarmConfigUpdateView.as_view(),
        name="alarm_edit",
    ),
    path(
        "alarms/<int:pk>/delete/",
        views.AlarmConfigDeleteView.as_view(),
        name="alarm_delete",
    ),
    # API endpoints
    path("api/export-json/", views.export_json, name="export_json"),
    path("api/get-logic-fields/", views.get_logic_fields, name="get_logic_fields"),
    path("api/ajax-sort-alarms/", views.ajax_sort_alarms, name="ajax_sort_alarms"),
    # API для справочников фильтров
    path("api/alarm-classes/", views.api_alarm_classes, name="api_alarm_classes"),
    path("api/logics/", views.api_logics, name="api_logics"),
    path("api/confirm-methods/", views.api_confirm_methods, name="api_confirm_methods"),
    path("api/limit-types/", views.api_limit_types, name="api_limit_types"),
    path(
        "api/limit-config-types/",
        views.api_limit_config_types,
        name="api_limit_config_types",
    ),
    path(
        "api/next-table-number/",
        views.api_next_table_number,
        name="api_next_table_number",
    ),
    path(
        "api/used-table-numbers/",
        views.api_used_table_numbers,
        name="api_used_table_numbers",
    ),
    path(
        "api/sort-fields/",
        views.api_sort_fields,
        name="api_sort_fields",
    ),
    path(
        "api/filter-fields/",
        views.api_filter_fields,
        name="api_filter_fields",
    ),
]
