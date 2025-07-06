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
    template_name = 'alarms/table_list.html'
    context_object_name = 'tables'


class AlarmTableCreateView(CreateView):
    """Представление для создания новой таблицы аварий"""
    model = AlarmTable
    form_class = AlarmTableForm
    template_name = 'alarms/table_form.html'
    success_url = reverse_lazy('alarms:table_list')


class AlarmTableUpdateView(UpdateView):
    """Представление для редактирования таблицы аварий"""
    model = AlarmTable
    form_class = AlarmTableForm
    template_name = 'alarms/table_form.html'
    success_url = reverse_lazy('alarms:table_list')


class AlarmTableDeleteView(DeleteView):
    """Представление для удаления таблицы аварий"""
    model = AlarmTable
    template_name = 'alarms/table_confirm_delete.html'
    success_url = reverse_lazy('alarms:table_list')


class AlarmConfigListView(ListView):
    """Представление для списка конфигураций аварий"""
    model = AlarmConfig
    template_name = 'alarms/alarm_list.html'
    context_object_name = 'alarms'
    paginate_by = 20

    def get_queryset(self):
        """Получаем queryset с поддержкой сортировки"""
        queryset = AlarmConfig.objects.select_related('table')
        
        # Получаем параметры сортировки
        sort_field = self.request.GET.get('sort', 'alarm_class')
        order = self.request.GET.get('order', 'asc')
        
        # Список разрешенных полей для сортировки
        allowed_fields = {
            'id': 'id',
            'alarm_class': 'alarm_class',
            'table': 'table__name',
            'logic': 'logic',
            'channel': 'channel',
            'msg': 'msg',
            'prior': 'prior',
            'created_at': 'created_at',
            'updated_at': 'updated_at'
        }
        
        # Проверяем, что поле разрешено для сортировки
        if sort_field in allowed_fields:
            field_name = allowed_fields[sort_field]
            if order == 'desc':
                field_name = f'-{field_name}'
            queryset = queryset.order_by(field_name)
        else:
            # По умолчанию сортируем по классу и приоритету
            queryset = queryset.order_by('alarm_class', 'prior')
        
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем режим отображения и параметры сортировки в контекст"""
        context = super().get_context_data(**kwargs)
        context['display_mode'] = self.request.GET.get('display_mode', 'compact')
        context['current_sort'] = self.request.GET.get('sort', 'alarm_class')
        context['current_order'] = self.request.GET.get('order', 'asc')
        return context


class AlarmTableDetailView(ListView):
    """Представление для отображения аварий конкретной таблицы"""
    model = AlarmConfig
    template_name = 'alarms/table_detail.html'
    context_object_name = 'alarms'
    paginate_by = 20

    def get_queryset(self):
        """Получаем аварии только для конкретной таблицы"""
        self.table = get_object_or_404(AlarmTable, pk=self.kwargs['table_id'])
        return AlarmConfig.objects.filter(table=self.table).order_by('alarm_class', 'prior')

    def get_context_data(self, **kwargs):
        """Добавляем информацию о таблице и режим отображения в контекст"""
        context = super().get_context_data(**kwargs)
        context['table'] = self.table
        context['display_mode'] = self.request.GET.get('display_mode', 'compact')
        return context


class AlarmConfigCreateView(CreateView):
    """Представление для создания новой конфигурации аварии"""
    model = AlarmConfig
    form_class = AlarmConfigForm
    template_name = 'alarms/alarm_form.html'
    success_url = reverse_lazy('alarms:alarm_list')

    def form_valid(self, form):
        messages.success(self.request, 'Аварийный сигнал успешно создан!')
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
    template_name = 'alarms/alarm_form.html'
    success_url = reverse_lazy('alarms:alarm_list')

    def form_valid(self, form):
        messages.success(self.request, 'Аварийный сигнал успешно обновлен!')
        return super().form_valid(form)


class AlarmConfigDeleteView(DeleteView):
    """Представление для удаления конфигурации аварии"""
    model = AlarmConfig
    template_name = 'alarms/alarm_confirm_delete.html'
    success_url = reverse_lazy('alarms:alarm_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Аварийный сигнал успешно удален!')
        return super().delete(request, *args, **kwargs)


def dashboard(request):
    """Главная страница приложения"""
    tables_count = AlarmTable.objects.count()
    alarms_count = AlarmConfig.objects.count()
    recent_alarms = AlarmConfig.objects.order_by('-created_at')[:5]
    
    context = {
        'tables_count': tables_count,
        'alarms_count': alarms_count,
        'recent_alarms': recent_alarms,
    }
    return render(request, 'alarms/dashboard.html', context)


@csrf_exempt
def export_json(request):
    """Экспорт конфигураций аварий в JSON файл"""
    if request.method == 'POST':
        try:
            # Получаем все конфигурации аварий
            alarms = AlarmConfig.objects.all().order_by('alarm_class', 'prior')
            
            # Формируем структуру данных для экспорта
            export_data = {
                'alarm_tables': [],
                'alarm_configs': []
            }
            
            # Добавляем таблицы аварий
            tables = AlarmTable.objects.all()
            for table in tables:
                export_data['alarm_tables'].append({
                    'id': table.id,
                    'name': table.name,
                    'description': table.description,
                    'created_at': table.created_at.isoformat(),
                    'updated_at': table.updated_at.isoformat()
                })
            
            # Добавляем конфигурации аварий
            for alarm in alarms:
                alarm_data = {
                    'id': alarm.id,
                    'alarm_class': alarm.alarm_class,
                    'table_id': alarm.table.id,
                    'logic': alarm.logic,
                    'event': alarm.event,
                    'channel': alarm.channel,
                    'limit_type': alarm.limit_type,
                    'low': alarm.low,
                    'high': alarm.high,
                    'discrete_val': alarm.discrete_val,
                    'msg': alarm.msg,
                    'hyst_low': alarm.hyst_low,
                    'hyst_high': alarm.hyst_high,
                    'ch_low': alarm.ch_low,
                    'ch_high': alarm.ch_high,
                    'confirm_method': alarm.confirm_method,
                    'prior': alarm.prior,
                    'created_at': alarm.created_at.isoformat(),
                    'updated_at': alarm.updated_at.isoformat()
                }
                export_data['alarm_configs'].append(alarm_data)
            
            # Создаем JSON ответ
            response = HttpResponse(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="alarm_config.json"'
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


@csrf_exempt
def get_logic_fields(request):
    """AJAX запрос для получения полей в зависимости от выбранной логики"""
    if request.method == 'POST':
        logic = request.POST.get('logic')
        
        # Определяем какие поля нужно показать/скрыть
        fields_config = {
            'event': {
                'show': ['event', 'msg', 'confirm_method', 'prior'],
                'hide': ['channel', 'limit_type', 'low', 'high', 'discrete_val', 
                        'hyst_low', 'hyst_high', 'ch_low', 'ch_high']
            },
            'discrete': {
                'show': ['channel', 'discrete_val', 'msg', 'confirm_method', 'prior'],
                'hide': ['event', 'limit_type', 'low', 'high', 'hyst_low', 
                        'hyst_high', 'ch_low', 'ch_high']
            },
            'analog': {
                'show': ['channel', 'limit_type', 'low', 'high', 'msg', 
                        'hyst_low', 'hyst_high', 'ch_low', 'ch_high', 
                        'confirm_method', 'prior'],
                'hide': ['event', 'discrete_val']
            },
            'change': {
                'show': ['channel', 'msg', 'confirm_method', 'prior'],
                'hide': ['event', 'limit_type', 'low', 'high', 'discrete_val', 
                        'hyst_low', 'hyst_high', 'ch_low', 'ch_high']
            }
        }
        
        return JsonResponse(fields_config.get(logic, {'show': [], 'hide': []}))
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
