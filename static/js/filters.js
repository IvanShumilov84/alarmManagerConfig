// Универсальный JS-модуль фильтрации для таблиц аварий

function applyFilters() {
    // Сбрасываем флаг блокировки восстановления
    preventAutoRestore = false;

    console.log('applyFilters вызвана');
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) {
        console.error('Форма фильтров не найдена!');
        return;
    }
    const url = new URL(window.location.href);
    // Сохраняем все не-фильтровые параметры
    const baseParams = [];
    for (const [key, value] of url.searchParams.entries()) {
        if (!key.startsWith('filter_')) {
            baseParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
        }
    }
    // Собираем только реально существующие строки фильтров и формируем индексы подряд
    const filterRows = document.querySelectorAll('.filter-row');
    console.log('Найдено строк фильтров:', filterRows.length);
    let hasFilters = false;
    const filtersData = [];
    let filterIndex = 0;
    const filterParams = [];
    filterRows.forEach((row, idx) => {
        const fieldSelect = row.querySelector('.filter-field');
        const opSelect = row.querySelector('.filter-op');
        if (!fieldSelect || !opSelect) {
            console.log(`Строка ${idx}: не найдены select'ы`);
            return;
        }
        const field = fieldSelect.value;
        const op = opSelect.value;
        let value = '';
        const valueInput = row.querySelector('.filter-value');
        if (valueInput) {
            value = valueInput.value.trim();
        }
        console.log(`Строка ${idx}: field=${field}, op=${op}, value=${value}`);
        // Фильтруем только валидные фильтры
        if (!field || !op) {
            console.log(`Строка ${idx}: пропущена - нет field или op`);
            return;
        }
        if (!value) {
            console.log(`Строка ${idx}: пропущена - нет value`);
            return;
        }
        filterParams.push(`filter_field_${filterIndex}=${encodeURIComponent(field)}`);
        filterParams.push(`filter_op_${filterIndex}=${encodeURIComponent(op)}`);
        filterParams.push(`filter_value_${filterIndex}=${encodeURIComponent(value)}`);
        hasFilters = true;
        filtersData.push({
            field: field,
            op: op,
            value: value
        });
        filterIndex++;
    });
    console.log('hasFilters:', hasFilters);
    console.log('filtersData:', filtersData);
    // Определяем ключ localStorage
    const storageKey = getStorageKey();
    if (hasFilters) {
        localStorage.setItem(storageKey, JSON.stringify(filtersData));
        console.log('Фильтры сохранены в localStorage:', JSON.stringify(filtersData));
    } else {
        localStorage.removeItem(storageKey);
        console.log('Фильтры удалены из localStorage');
    }
    // Собираем итоговый query string
    let queryString = '';
    if (baseParams.length > 0 || filterParams.length > 0) {
        queryString = '?' + [...baseParams, ...filterParams].join('&');
    }
    // Формируем итоговый URL
    const finalUrl = url.origin + url.pathname + queryString;
    console.log('Переход на URL:', finalUrl);
    window.location.href = finalUrl;
    updateActiveNotices();
}

function clearFilters() {
    // Блокируем автоматическое восстановление
    preventAutoRestore = true;

    console.log('clearFilters вызвана');

    const filterFieldsContainer = document.getElementById('filterFields');
    if (filterFieldsContainer) {
        filterFieldsContainer.innerHTML = '';
        addFilterField();
    }

    // Удаляем все возможные ключи фильтров из localStorage для текущей страницы
    const storageKey = getStorageKey();
    const oldKeys = getOldStorageKeys();

    localStorage.removeItem(storageKey);
    localStorage.removeItem(oldKeys.fields);
    localStorage.removeItem(oldKeys.operators);
    localStorage.removeItem(oldKeys.values);

    console.log('Все ключи фильтров удалены из localStorage для текущей страницы');

    // Строим URL без параметров фильтрации
    const url = new URL(window.location.href);
    for (const key of Array.from(url.searchParams.keys())) {
        if (key.startsWith('filter_')) {
            url.searchParams.delete(key);
        }
    }

    console.log('Переход на URL без фильтров:', url.toString());
    window.location.href = url.toString();
    updateActiveNotices();
}

function restoreFilters() {
    const storageKey = getStorageKey();
    const savedFilters = localStorage.getItem(storageKey);
    let filtersData = [];
    if (savedFilters) {
        try {
            filtersData = JSON.parse(savedFilters);
        } catch (e) {
            localStorage.removeItem(storageKey);
        }
    }
    const filterFieldsContainer = document.getElementById('filterFields');
    if (!filterFieldsContainer) {
        console.error('Контейнер фильтров не найден!');
        return;
    }
    filterFieldsContainer.innerHTML = '';
    for (let i = 0; i < filtersData.length; i++) {
        const filter = filtersData[i];
        addFilterField(i, filter.field, filter.op, filter.value);
    }
    if (filtersData.length === 0) {
        addFilterField();
    }
    updateActiveNotices();
}

function updateFilterOperators(index, skipRangeRestore = false) {
    const row = document.querySelectorAll('.filter-row')[index];
    if (!row) return;
    const fieldSelect = row.querySelector('.filter-field');
    const opSelect = row.querySelector('.filter-op');
    if (!fieldSelect || !opSelect) return;
    const field = fieldSelect.value;
    const currentOp = opSelect.value;
    opSelect.innerHTML = '';
    if (field === 'id' || field === 'alarms_count') {
        opSelect.innerHTML = `
            <option value="exact">Точно</option>
            <option value="gt">Больше</option>
            <option value="lt">Меньше</option>
            <option value="gte">Больше или равно</option>
            <option value="lte">Меньше или равно</option>
        `;
    } else if (field === 'created_at' || field === 'updated_at') {
        opSelect.innerHTML = `
            <option value="exact">Равно</option>
            <option value="gt">Больше</option>
            <option value="lt">Меньше</option>
            <option value="gte">Больше или равно</option>
            <option value="lte">Меньше или равно</option>
            <option value="range">Диапазон</option>
        `;
        if (currentOp && ['exact', 'gt', 'lt', 'gte', 'lte', 'range'].includes(currentOp)) {
            // Если skipRangeRestore = true и оператор был оператором сравнения, не восстанавливаем его
            if (skipRangeRestore && ['gt', 'lt', 'gte', 'lte', 'range'].includes(currentOp)) {
                opSelect.value = 'exact';
            } else {
                opSelect.value = currentOp;
            }
            setTimeout(() => updateFilterValueType(index), 0);
        }
        const valueInput = row.querySelector('.filter-value');
        if (valueInput) {
            valueInput.type = 'date';
            valueInput.placeholder = 'ГГГГ-ММ-ДД';
        }
    } else {
        opSelect.innerHTML = `
            <option value="exact">Точно</option>
            <option value="contains">Содержит</option>
            <option value="startswith">Начинается с</option>
            <option value="endswith">Заканчивается на</option>
        `;
        // Восстанавливаем выбранный оператор для всех полей
        if (currentOp && ['exact', 'contains', 'startswith', 'endswith'].includes(currentOp)) {
            opSelect.value = currentOp;
        }
    }
    // ГАРАНТИРОВАННО обновляем виджет значения при смене поля
    updateFilterValueType(index);
}

function updateFilterValueType(index) {
    const row = document.querySelectorAll('.filter-row')[index];
    if (!row) {
        return;
    }
    const fieldSelect = row.querySelector('.filter-field');
    const opSelect = row.querySelector('.filter-op');
    if (!fieldSelect || !opSelect) {
        return;
    }
    const selectedField = fieldSelect.value;
    const selectedOp = opSelect.value;
    const valueContainer = row.querySelector('.col-md-3:nth-child(3)');
    if (!valueContainer) return;
    if (selectedField === 'created_at' || selectedField === 'updated_at') {
        let currentValue = '';
        const startValue = row.querySelector('.filter-value-start');
        const endValue = row.querySelector('.filter-value-end');
        const valueInput = row.querySelector('.filter-value');
        if (startValue && endValue) {
            const start = startValue.value;
            const end = endValue.value;
            if (start || end) {
                currentValue = `${start}|${end}`;
            }
        } else if (valueInput) {
            currentValue = valueInput.value;
        }
        if (selectedOp === 'range') {
            valueContainer.innerHTML = `
                <div class="row g-1">
                    <div class="col-6">
                        <input type="date" name="filter_value_${index}_start" class="form-control form-control-sm filter-value-start" placeholder="От">
                    </div>
                    <div class="col-6">
                        <input type="date" name="filter_value_${index}_end" class="form-control form-control-sm filter-value-end" placeholder="До">
                    </div>
                </div>
            `;
            if (currentValue && currentValue.includes('|')) {
                const [start, end] = currentValue.split('|');
                const startInput = valueContainer.querySelector('.filter-value-start');
                const endInput = valueContainer.querySelector('.filter-value-end');
                if (startInput && start) startInput.value = start;
                if (endInput && end) endInput.value = end;
            } else if (currentValue) {
                const startInput = valueContainer.querySelector('.filter-value-start');
                if (startInput) startInput.value = currentValue;
            }
        } else {
            valueContainer.innerHTML = `
                <input type="date" name="filter_value_${index}" class="form-control form-control-sm filter-value" placeholder="ГГГГ-ММ-ДД">
            `;
            const newValueInput = valueContainer.querySelector('.filter-value');
            if (newValueInput) {
                // Если переключаемся с range на другой оператор, не восстанавливаем значение
                if (currentValue && currentValue.includes('|') && selectedOp !== 'range') {
                    // Очищаем значение при переключении с диапазона
                    newValueInput.value = '';
                } else if (currentValue && !currentValue.includes('|')) {
                    newValueInput.value = currentValue;
                }
            }
        }
    } else if (selectedField === 'id' || selectedField === 'alarms_count') {
        // Пересоздаём input для числовых/текстовых полей
        valueContainer.innerHTML = `<input type="number" name="filter_value_${index}" class="form-control form-control-sm filter-value" placeholder="Число">`;
        // Если оператор не числовой, делаем текстовое поле
        if (!['gt', 'lt', 'gte', 'lte', 'exact'].includes(selectedOp)) {
            valueContainer.innerHTML = `<input type="text" name="filter_value_${index}" class="form-control form-control-sm filter-value" placeholder="Значение">`;
        }
    } else {
        // Пересоздаём input для обычных текстовых полей
        valueContainer.innerHTML = `<input type="text" name="filter_value_${index}" class="form-control form-control-sm filter-value" placeholder="Значение">`;
    }
}

// Наборы полей для фильтрации
const FILTER_FIELDS = {
    tables: [
        { value: 'id', label: 'ID' },
        { value: 'name', label: 'Название' },
        { value: 'description', label: 'Описание' },
        { value: 'alarms_count', label: 'Количество аварий' },
        { value: 'created_at', label: 'Дата создания' },
        { value: 'updated_at', label: 'Дата обновления' },
    ],
    alarms: [
        { value: 'id', label: 'ID' },
        { value: 'alarm_class', label: 'Класс' },
        { value: 'table', label: 'Таблица' },
        { value: 'logic', label: 'Логика' },
        { value: 'channel', label: 'Канал' },
        { value: 'msg', label: 'Сообщение' },
        { value: 'prior', label: 'Приоритет' },
        { value: 'created_at', label: 'Дата создания' },
        { value: 'updated_at', label: 'Дата обновления' },
    ]
};

function getCurrentFilterFields() {
    const path = window.location.pathname;
    if (path.includes('/alarms/')) {
        return FILTER_FIELDS.alarms;
    } else if (path.includes('/tables/')) {
        return FILTER_FIELDS.tables;
    }
    // По умолчанию — поля для tables
    return FILTER_FIELDS.tables;
}

function addFilterField(index = null, fieldValue = '', operatorValue = '', valueValue = '') {
    const filterFields = document.getElementById('filterFields');
    if (!filterFields) {
        console.error('Контейнер filterFields не найден!');
        return;
    }
    const currentCount = filterFields.querySelectorAll('.filter-row').length;
    const idx = index !== null ? index : currentCount;
    const fields = getCurrentFilterFields();
    let optionsHtml = '<option value="">Выберите поле</option>';
    for (const f of fields) {
        optionsHtml += `<option value="${f.value}" ${fieldValue === f.value ? 'selected' : ''}>${f.label}</option>`;
    }
    const row = document.createElement('div');
    row.className = 'row mb-2 filter-row';
    row.innerHTML = `
        <div class="col-md-3 mb-1">
            <select name="filter_field_${idx}" class="form-select form-select-sm filter-field" onchange="updateFilterOperators(${idx})">
                ${optionsHtml}
            </select>
        </div>
        <div class="col-md-3 mb-1">
            <select name="filter_op_${idx}" class="form-select form-select-sm filter-op" onchange="updateFilterValueType(${idx})">
                <option value="exact" ${operatorValue === 'exact' ? 'selected' : ''}>Точно</option>
                <option value="contains" ${operatorValue === 'contains' ? 'selected' : ''}>Содержит</option>
                <option value="startswith" ${operatorValue === 'startswith' ? 'selected' : ''}>Начинается с</option>
                <option value="endswith" ${operatorValue === 'endswith' ? 'selected' : ''}>Заканчивается на</option>
                <option value="gt" ${operatorValue === 'gt' ? 'selected' : ''}>Больше</option>
                <option value="lt" ${operatorValue === 'lt' ? 'selected' : ''}>Меньше</option>
                <option value="gte" ${operatorValue === 'gte' ? 'selected' : ''}>Больше или равно</option>
                <option value="lte" ${operatorValue === 'lte' ? 'selected' : ''}>Меньше или равно</option>
                <option value="range" ${operatorValue === 'range' ? 'selected' : ''}>Диапазон</option>
            </select>
        </div>
        <div class="col-md-3 mb-1">
            <input type="text" name="filter_value_${idx}" class="form-control form-control-sm filter-value" value="${valueValue}" placeholder="Значение">
        </div>
        <div class="col-md-3 mb-1 d-flex align-items-center">
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFilter(this)" title="Удалить фильтр">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    filterFields.appendChild(row);

    // Интеграция с динамическими фильтрами
    if (typeof shouldUseSelect === 'function' && typeof replaceInputWithSelect === 'function') {
        if (fieldValue && shouldUseSelect(fieldValue)) {
            replaceInputWithSelect(row, fieldValue, valueValue, idx);
        }
    }

    // Если поле уже выбрано, обновляем операторы и тип значения
    if (fieldValue) {
        updateFilterOperators(idx);
        if (operatorValue) {
            const opSelect = row.querySelector('.filter-op');
            if (opSelect) {
                // Устанавливаем оператор после обновления списка операторов
                opSelect.value = operatorValue;
            }
        }
        setTimeout(() => updateFilterValueType(idx), 0);
        // Явно выставляем значение после обновления виджета
        if (valueValue) {
            if (operatorValue === 'range' && (fieldValue === 'created_at' || fieldValue === 'updated_at')) {
                const parts = valueValue.split('|');
                if (parts.length === 2) {
                    setTimeout(() => {
                        const startInput = row.querySelector(`input[name="filter_value_${idx}_start"]`);
                        const endInput = row.querySelector(`input[name="filter_value_${idx}_end"]`);
                        if (startInput) startInput.value = parts[0];
                        if (endInput) endInput.value = parts[1];
                    }, 0);
                }
            } else {
                setTimeout(() => {
                    const valueInput = row.querySelector('.filter-value');
                    if (valueInput) valueInput.value = valueValue;
                }, 0);
            }
        }
    }
    updateActiveNotices();
}

function updateActiveNotices() {
    // Фильтры
    const filtersActiveNotice = document.getElementById('filtersActiveNotice');
    const urlParams = new URLSearchParams(window.location.search);
    const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_field_'));
    if (filtersActiveNotice) {
        filtersActiveNotice.style.display = hasUrlFilters ? 'inline-block' : 'none';
    }
}

function toggleFilterSettings() {
    const filterSettingsBody = document.getElementById('filterSettingsBody');
    const filterToggleIcon = document.getElementById('filterToggleIcon');
    if (!filterSettingsBody || !filterToggleIcon) return;

    // Получаем правильный ключ для сохранения состояния
    const path = window.location.pathname;
    const settingsKey = path.includes('/alarms/') ? 'alarmsFilterSettingsExpanded' : 'tablesFilterSettingsExpanded';

    if (filterSettingsBody.style.display === 'none' || filterSettingsBody.style.display === '') {
        filterSettingsBody.style.display = 'block';
        filterToggleIcon.className = 'bi bi-chevron-down';
        localStorage.setItem(settingsKey, 'true');
    } else {
        filterSettingsBody.style.display = 'none';
        filterToggleIcon.className = 'bi bi-chevron-right';
        localStorage.setItem(settingsKey, 'false');
    }
    const filtersActiveNotice = document.getElementById('filtersActiveNotice');
    if (filterSettingsBody.style.display === 'none' || filterSettingsBody.style.display === '') {
        if (filtersActiveNotice) filtersActiveNotice.style.display = 'none';
    } else {
        let active = false;
        document.querySelectorAll('.filter-row').forEach(row => {
            const field = row.querySelector('.filter-field');
            const op = row.querySelector('.filter-op');
            const val = row.querySelector('.filter-value');
            if (field && field.value && op && op.value && val && val.value) active = true;
        });
        if (filtersActiveNotice) filtersActiveNotice.style.display = active ? 'block' : 'none';
    }
    updateActiveNotices();
}

function removeFilter(button) {
    // Блокируем автоматическое восстановление при удалении фильтра
    preventAutoRestore = true;

    console.log('removeFilter вызвана');

    const row = button.closest('.filter-row');
    if (row) {
        row.remove();
        // Проверяем, остались ли еще строки фильтров
        const filterFields = document.getElementById('filterFields');
        const remainingRows = filterFields.querySelectorAll('.filter-row');

        // Если не осталось ни одной строки, полностью сбрасываем фильтры
        if (remainingRows.length === 0) {
            console.log('Нет оставшихся фильтров, вызываем clearFilters');
            clearFilters();
            return;
        } else {
            // Просто обновляем индексы оставшихся строк
            remainingRows.forEach((row, index) => {
                // Обновляем name атрибуты
                const fieldSelect = row.querySelector('.filter-field');
                const opSelect = row.querySelector('.filter-op');
                const valueInput = row.querySelector('.filter-value');

                if (fieldSelect) fieldSelect.name = `filter_field_${index}`;
                if (opSelect) opSelect.name = `filter_op_${index}`;
                if (valueInput) valueInput.name = `filter_value_${index}`;

                // Обновляем обработчики событий
                if (fieldSelect) {
                    fieldSelect.onchange = () => updateFilterOperators(index);
                }
                if (opSelect) {
                    opSelect.onchange = () => updateFilterValueType(index);
                }
            });

            updateActiveNotices();

            // Автоматически применяем фильтры после удаления
            console.log('Применяем фильтры после удаления');
            setTimeout(() => {
                applyFilters();
            }, 100);
        }
    }
}

// Флаг для предотвращения автоматического восстановления фильтров
let preventAutoRestore = false;

// Функция для получения правильного ключа localStorage в зависимости от страницы
function getStorageKey() {
    const path = window.location.pathname;
    if (path.includes('/alarms/')) {
        return 'alarms_filters';
    } else if (path.includes('/tables/')) {
        return 'tables_filters';
    }
    // По умолчанию — ключ для tables
    return 'tables_filters';
}

// Функция для получения старых ключей localStorage в зависимости от страницы
function getOldStorageKeys() {
    const path = window.location.pathname;
    if (path.includes('/alarms/')) {
        return {
            fields: 'alarmFilterFields',
            operators: 'alarmFilterOperators',
            values: 'alarmFilterValues'
        };
    } else if (path.includes('/tables/')) {
        return {
            fields: 'tableFilterFields',
            operators: 'tableFilterOperators',
            values: 'tableFilterValues'
        };
    }
    // По умолчанию — ключи для tables
    return {
        fields: 'tableFilterFields',
        operators: 'tableFilterOperators',
        values: 'tableFilterValues'
    };
}

function restoreFiltersUniversal() {
    // Если восстановление заблокировано, не восстанавливаем
    if (preventAutoRestore) {
        console.log('Автоматическое восстановление фильтров заблокировано');
        return;
    }

    console.log('restoreFiltersUniversal вызвана');
    const urlParams = new URLSearchParams(window.location.search);
    const filterFieldsContainer = document.getElementById('filterFields');
    if (!filterFieldsContainer) {
        console.error('Контейнер фильтров не найден!');
        return;
    }
    // Проверяем, есть ли параметры фильтрации в URL
    const urlFilters = [];
    let i = 0;
    while (true) {
        const field = urlParams.get(`filter_field_${i}`);
        const op = urlParams.get(`filter_op_${i}`);
        const value = urlParams.get(`filter_value_${i}`);
        if (!field || !op || !value) break;
        urlFilters.push({ field, op, value });
        i++;
    }
    console.log('URL фильтры:', urlFilters);
    filterFieldsContainer.innerHTML = '';
    if (urlFilters.length > 0) {
        // Восстанавливаем из URL
        console.log('Восстанавливаем фильтры из URL');
        urlFilters.forEach((f, idx) => {
            console.log(`Восстанавливаем фильтр ${idx}:`, f);
            addFilterField(idx, f.field, f.op, f.value);
        });
        updateActiveNotices();
    } else {
        // Восстанавливаем из localStorage и применяем
        console.log('Восстанавливаем фильтры из localStorage');
        restoreFilters();

        // Проверяем старые ключи localStorage
        const oldKeys = getOldStorageKeys();
        const fields = localStorage.getItem(oldKeys.fields);
        const operators = localStorage.getItem(oldKeys.operators);
        const values = localStorage.getItem(oldKeys.values);

        console.log('Старые ключи:', { fields, operators, values });

        if (fields && operators && values) {
            try {
                const fieldsData = JSON.parse(fields);
                const operatorsData = JSON.parse(operators);
                const valuesData = JSON.parse(values);

                console.log('Данные из старых ключей:', { fieldsData, operatorsData, valuesData });

                if (Array.isArray(fieldsData) && fieldsData.length > 0) {
                    console.log('Восстанавливаем фильтры из старых ключей');
                    const filterFieldsContainer = document.getElementById('filterFields');
                    if (filterFieldsContainer) {
                        filterFieldsContainer.innerHTML = '';
                        for (let i = 0; i < fieldsData.length; i++) {
                            const field = fieldsData[i];
                            const op = operatorsData[i] || 'exact';
                            const value = valuesData[i] || '';
                            if (field && op && value) {
                                addFilterField(i, field, op, value);
                            }
                        }
                        updateActiveNotices();
                        // Проверяем, есть ли уже фильтры в URL
                        const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_field_'));
                        if (!hasUrlFilters) {
                            // Применяем фильтры автоматически с небольшой задержкой
                            console.log('Фильтры восстановлены из старых ключей, применяем их');
                            setTimeout(() => {
                                applyFilters();
                            }, 200);
                        } else {
                            console.log('Фильтры уже есть в URL, не применяем автоматически');
                        }
                        return;
                    }
                }
            } catch (e) {
                console.log('Ошибка при парсинге старых ключей:', e);
            }
        }

        // Если старые ключи не работают, пробуем новый ключ
        const storageKey = getStorageKey();
        console.log('Ищем ключ:', storageKey);
        console.log('Все ключи localStorage:', Object.keys(localStorage));
        const savedFilters = localStorage.getItem(storageKey);
        console.log('Сохранённые фильтры из localStorage:', savedFilters);
        if (savedFilters) {
            try {
                const filtersData = JSON.parse(savedFilters);
                console.log('Распарсенные фильтры:', filtersData);
                if (Array.isArray(filtersData) && filtersData.length > 0) {
                    // Проверяем, есть ли уже фильтры в URL
                    const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_field_'));
                    if (!hasUrlFilters) {
                        console.log('Фильтры найдены в localStorage, применяем их');
                        // Применяем фильтры автоматически с небольшой задержкой
                        setTimeout(() => {
                            applyFilters();
                        }, 200);
                    } else {
                        console.log('Фильтры уже есть в URL, не применяем автоматически');
                    }
                } else {
                    console.log('Фильтры не прошли проверку: не массив или пустой');
                }
            } catch (e) {
                console.log('Ошибка при парсинге фильтров:', e);
            }
        } else {
            console.log('В localStorage нет сохранённых фильтров');
            // Проверяем все ключи, содержащие "filter"
            const filterKeys = Object.keys(localStorage).filter(key => key.includes('filter'));
            console.log('Ключи с "filter":', filterKeys);
            filterKeys.forEach(key => {
                console.log(`Ключ ${key}:`, localStorage.getItem(key));
            });
        }
    }
}

// === Обработчики событий фильтрации ===
document.addEventListener('DOMContentLoaded', () => {
    restoreFiltersUniversal();

    // Восстанавливаем состояние спойлера фильтров
    const path = window.location.pathname;
    const settingsKey = path.includes('/alarms/') ? 'alarmsFilterSettingsExpanded' : 'tablesFilterSettingsExpanded';
    const filterSettingsBody = document.getElementById('filterSettingsBody');
    const filterToggleIcon = document.getElementById('filterToggleIcon');

    if (filterSettingsBody && filterToggleIcon) {
        const isExpanded = localStorage.getItem(settingsKey) === 'true';
        if (isExpanded) {
            filterSettingsBody.style.display = 'block';
            filterToggleIcon.className = 'bi bi-chevron-down';
        } else {
            filterSettingsBody.style.display = 'none';
            filterToggleIcon.className = 'bi bi-chevron-right';
        }
    }

    // Делегирование для .keep-filters
    document.addEventListener('click', function (event) {
        if (event.target.closest('a.keep-filters')) {
            event.preventDefault();
            const link = event.target.closest('a.keep-filters');
            const url = new URL(link.href, window.location.origin);
            const currentParams = new URLSearchParams(window.location.search);
            for (const [key, value] of currentParams.entries()) {
                if (key.startsWith('filter_')) {
                    url.searchParams.set(key, value);
                }
            }
            if (currentParams.has('display_mode')) {
                url.searchParams.set('display_mode', currentParams.get('display_mode'));
            }
            if (url.toString() !== link.href) {
                window.location.href = url.toString();
            } else {
                window.location.href = link.href;
            }
        }
    });
    // Enter в .filter-value
    document.addEventListener('keypress', function (event) {
        if (event.target.classList.contains('filter-value') && event.key === 'Enter') {
            event.preventDefault();
            applyFilters();
        }
    });
    // Кнопка "Применить фильтры"
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function () {
            applyFilters();
        });
    }
});

// Обработчик для восстановления фильтров при возврате на страницу
window.addEventListener('pageshow', (event) => {
    // Восстанавливаем фильтры при каждом показе страницы
    restoreFiltersUniversal();
});

// Дополнительный обработчик для случаев, когда pageshow не срабатывает
window.addEventListener('focus', () => {
    // Небольшая задержка для гарантии, что DOM готов
    setTimeout(() => {
        restoreFiltersUniversal();
    }, 100);
}); 