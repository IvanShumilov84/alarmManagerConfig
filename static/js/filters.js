// Универсальный JS-модуль фильтрации для таблиц аварий

function applyFilters() {
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
    let hasFilters = false;
    const filtersData = [];
    let filterIndex = 0;
    const filterParams = [];
    filterRows.forEach(row => {
        const fieldSelect = row.querySelector('.filter-field');
        const opSelect = row.querySelector('.filter-op');
        if (!fieldSelect || !opSelect) return;
        const field = fieldSelect.value;
        const op = opSelect.value;
        let value = '';
        const startValue = row.querySelector('.filter-value-start');
        const endValue = row.querySelector('.filter-value-end');
        if (startValue && endValue && op === 'range') {
            const start = startValue.value.trim();
            const end = endValue.value.trim();
            value = `${start}|${end}`;
        } else {
            const valueInput = row.querySelector('.filter-value');
            if (valueInput) {
                value = valueInput.value.trim();
            }
        }
        const isDateField = field === 'created_at' || field === 'updated_at';
        // Фильтруем только валидные фильтры
        if (!field || !op) return;
        if (!isDateField && !value) return;
        filterParams.push(`filter_field_${filterIndex}=${encodeURIComponent(field)}`);
        filterParams.push(`filter_op_${filterIndex}=${encodeURIComponent(op)}`);
        if (op === 'range' && value.includes('|')) {
            const [start, end] = value.split('|');
            filterParams.push(`filter_value_${filterIndex}_start=${encodeURIComponent(start || '')}`);
            filterParams.push(`filter_value_${filterIndex}_end=${encodeURIComponent(end || '')}`);
            filterParams.push(`filter_value_${filterIndex}=${encodeURIComponent(start || '')}`);
        } else {
            filterParams.push(`filter_value_${filterIndex}=${encodeURIComponent(value)}`);
        }
        hasFilters = true;
        filtersData.push({
            field: field,
            op: op,
            value: value
        });
        filterIndex++;
    });

    // Определяем ключ localStorage в зависимости от страницы
    const storageKey = getCurrentFilterFields() === FILTER_FIELDS.alarms ? 'alarms_filters' : 'tables_filters';

    if (hasFilters) {
        localStorage.setItem(storageKey, JSON.stringify(filtersData));
    } else {
        localStorage.removeItem(storageKey);
    }
    // Собираем итоговый query string
    let queryString = '';
    if (baseParams.length > 0 || filterParams.length > 0) {
        queryString = '?' + [...baseParams, ...filterParams].join('&');
    }
    // Формируем итоговый URL
    const finalUrl = url.origin + url.pathname + queryString;
    window.location.href = finalUrl;
    updateActiveNotices();
}

function clearFilters() {
    const filterFieldsContainer = document.getElementById('filterFields');
    if (filterFieldsContainer) {
        filterFieldsContainer.innerHTML = '';
        addFilterField();
    }

    // Определяем ключи localStorage и sessionStorage в зависимости от страницы
    const storageKey = getCurrentFilterFields() === FILTER_FIELDS.alarms ? 'alarms_filters' : 'tables_filters';
    const clearingKey = getCurrentFilterFields() === FILTER_FIELDS.alarms ? 'clearing_alarms_filters' : 'clearing_tables_filters';

    localStorage.removeItem(storageKey);
    sessionStorage.setItem(clearingKey, 'true');

    // Строим URL без параметров фильтрации
    const url = new URL(window.location.href);

    // Удаляем все параметры фильтрации
    for (const key of Array.from(url.searchParams.keys())) {
        if (key.startsWith('filter_')) {
            url.searchParams.delete(key);
        }
    }

    // Переходим по очищенному URL
    window.location.href = url.toString();
}

function restoreFilters() {
    // Определяем ключи в зависимости от страницы
    const storageKey = getCurrentFilterFields() === FILTER_FIELDS.alarms ? 'alarms_filters' : 'tables_filters';
    const clearingKey = getCurrentFilterFields() === FILTER_FIELDS.alarms ? 'clearing_alarms_filters' : 'clearing_tables_filters';

    sessionStorage.removeItem(clearingKey);

    const savedFilters = localStorage.getItem(storageKey);

    let filtersData = [];
    let shouldApplyFilters = false;
    if (savedFilters) {
        try {
            filtersData = JSON.parse(savedFilters);
            const urlParams = new URLSearchParams(window.location.search);
            const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_'));
            if (filtersData.length > 0 && !hasUrlFilters) {
                shouldApplyFilters = true;
            }
        } catch (e) {
            console.error('Ошибка при парсинге фильтров из localStorage:', e);
            localStorage.removeItem(storageKey);
        }
    }
    const isClearing = sessionStorage.getItem(clearingKey);
    if (filtersData.length === 0 && !isClearing) {
        const urlParams = new URLSearchParams(window.location.search);
        const filterFields = [];
        const filterOps = [];
        const filterValues = [];
        const filterValuesStart = [];
        const filterValuesEnd = [];
        for (const [key, value] of urlParams.entries()) {
            if (key.startsWith('filter_field_')) {
                const index = key.replace('filter_field_', '');
                filterFields[index] = value;
            } else if (key.startsWith('filter_op_')) {
                const index = key.replace('filter_op_', '');
                filterOps[index] = value;
            } else if (key.startsWith('filter_value_') && !key.includes('_start') && !key.includes('_end')) {
                const index = key.replace('filter_value_', '');
                filterValues[index] = value;
            } else if (key.startsWith('filter_value_') && key.includes('_start')) {
                const index = key.replace('filter_value_', '').replace('_start', '');
                filterValuesStart[index] = value;
            } else if (key.startsWith('filter_value_') && key.includes('_end')) {
                const index = key.replace('filter_value_', '').replace('_end', '');
                filterValuesEnd[index] = value;
            }
        }
        const maxIndex = Math.max(filterFields.length, filterOps.length, filterValues.length);
        for (let i = 0; i < maxIndex; i++) {
            const field = filterFields[i] || '';
            const op = filterOps[i] || '';
            let value = filterValues[i] || '';
            if (op === 'range' && (filterValuesStart[i] || filterValuesEnd[i])) {
                const start = filterValuesStart[i] || '';
                const end = filterValuesEnd[i] || '';
                value = `${start}|${end}`;
            }
            if (field || op || value) {
                filtersData.push({
                    field: field,
                    op: op,
                    value: value
                });
            }
        }
        if (filtersData.length > 0) {
            localStorage.setItem(storageKey, JSON.stringify(filtersData));
        }
    }
    const filterFieldsContainer = document.getElementById('filterFields');
    if (!filterFieldsContainer) {
        console.error('Контейнер фильтров не найден!');
        return;
    }
    filterFieldsContainer.innerHTML = '';
    const updatedFiltersData = [];
    for (let i = 0; i < filtersData.length; i++) {
        const filter = filtersData[i];
        addFilterField(i, filter.field, filter.op, filter.value);

        // Сохраняем данные для localStorage без изменений
        if (filter.field && filter.value) {
            updatedFiltersData.push({
                field: filter.field,
                op: filter.op,
                value: filter.value
            });
        }
    }

    // Обновляем localStorage с исправленными данными
    if (updatedFiltersData.length > 0) {
        localStorage.setItem(storageKey, JSON.stringify(updatedFiltersData));
    } else {
        localStorage.removeItem(storageKey);
    }
    if (filtersData.length > 0) {
        const filterSettingsBody = document.getElementById('filterSettingsBody');
        const filterToggleIcon = document.getElementById('filterToggleIcon');
        if (filterSettingsBody && filterToggleIcon) {
            filterSettingsBody.style.display = 'block';
            filterToggleIcon.className = 'bi bi-chevron-down';
        }
    }
    if (filtersData.length === 0) {
        addFilterField();
    }
    if (shouldApplyFilters && filtersData.length > 0) {
        setTimeout(() => {
            applyFilters();
        }, 100);
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
    // Сортировка
    const sortActiveNotice = document.getElementById('sortActiveNotice');
    let sortActive = false;
    document.querySelectorAll('.sort-field').forEach(f => { if (f.value) sortActive = true; });
    if (sortActiveNotice) {
        sortActiveNotice.style.display = sortActive ? 'inline-block' : 'none';
    }
    // Фильтры
    const filtersActiveNotice = document.getElementById('filtersActiveNotice');
    // Проверяем фильтры в URL
    const urlParams = new URLSearchParams(window.location.search);
    const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_field_'));
    // Показываем бейдж только если есть фильтры в URL
    if (filtersActiveNotice) {
        filtersActiveNotice.style.display = hasUrlFilters ? 'inline-block' : 'none';
    }
}

function toggleFilterSettings() {
    const filterSettingsBody = document.getElementById('filterSettingsBody');
    const filterToggleIcon = document.getElementById('filterToggleIcon');
    if (!filterSettingsBody || !filterToggleIcon) return;
    if (filterSettingsBody.style.display === 'none' || filterSettingsBody.style.display === '') {
        filterSettingsBody.style.display = 'block';
        filterToggleIcon.className = 'bi bi-chevron-down';
        localStorage.setItem('tablesFilterSettingsExpanded', 'true');
    } else {
        filterSettingsBody.style.display = 'none';
        filterToggleIcon.className = 'bi bi-chevron-right';
        localStorage.setItem('tablesFilterSettingsExpanded', 'false');
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
    const row = button.closest('.filter-row');
    if (row) {
        row.remove();
        // Проверяем, остались ли еще строки фильтров
        const filterFields = document.getElementById('filterFields');
        const remainingRows = filterFields.querySelectorAll('.filter-row');

        // Если не осталось ни одной строки, полностью сбрасываем фильтры
        if (remainingRows.length === 0) {
            clearFilters();
            return;
        } else {
            // После удаления фильтра пересоздаём все строки фильтров для корректных индексов
            const filtersData = [];
            remainingRows.forEach((row) => {
                const fieldSelect = row.querySelector('.filter-field');
                const opSelect = row.querySelector('.filter-op');
                const valueInput = row.querySelector('.filter-value');
                if (fieldSelect && fieldSelect.value && opSelect && opSelect.value) {
                    const field = fieldSelect.value;
                    const op = opSelect.value;
                    let value = '';
                    if (valueInput) {
                        value = valueInput.value.trim();
                    }
                    filtersData.push({ field, op, value });
                }
            });
            // Очищаем контейнер и пересоздаём строки фильтров с правильными индексами
            filterFields.innerHTML = '';
            filtersData.forEach((f, i) => {
                addFilterField(i, f.field, f.op, f.value);
            });
            updateActiveNotices();
            // После пересоздания DOM сразу вызываем applyFilters для применения фильтрации
            setTimeout(applyFilters, 0);
            return;
        }
    }
} 