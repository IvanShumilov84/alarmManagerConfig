from .views import get_tables_count, get_alarms_count


def sidebar_data(request):
    """Контекст-процессор для добавления данных сайдбара во все шаблоны"""
    return {
        "sidebar_tables_count": get_tables_count(),
        "sidebar_alarms_count": get_alarms_count(),
    }
