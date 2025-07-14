// Универсальный JS-модуль фильтрации для таблиц аварий

function applyFilters() {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) {
        console.error('Форма фильтров не найдена!');
        return;
    }
    const url = new URL(window.location.href);
    for (const key of url.searchParams.keys()) {
        if (key.startsWith('filter_')) {
            url.searchParams.delete(key);
        }
    }
    const filterFields = filterForm.querySelectorAll('.filter-field');
    const filterOps = filterForm.querySelectorAll('.filter-op');
    let hasFilters = false;
    const filtersData = [];
    let filterIndex = 0;
    for (let i = 0; i < filterFields.length; i++) {
        const field = filterFields[i].value;
        const op = filterOps[i] ? filterOps[i].value : 'exact';
        let value = '';
        const filterRow = filterFields[i].closest('.filter-row');
        if (filterRow) {
            const startValue = filterRow.querySelector('.filter-value-start');
            const endValue = filterRow.querySelector('.filter-value-end');
            if (startValue && endValue && op === 'range') {
                const start = startValue.value.trim();
                const end = endValue.value.trim();
                value = `${start}|${end}`;
            } else {
                const valueInput = filterRow.querySelector('.filter-value');
                if (valueInput) {
                    value = valueInput.value.trim();
                }
            }
        }
        const isDateField = field === 'created_at' || field === 'updated_at';
        const isValidFilter = field && (
            (isDateField) ||
            (value && value !== '')
        );
        if (isValidFilter) {
            url.searchParams.set(`filter_field_${filterIndex}`, field);
            url.searchParams.set(`filter_op_${filterIndex}`, op);
            if (op === 'range' && value.includes('|')) {
                const [start, end] = value.split('|');
                url.searchParams.set(`filter_value_${filterIndex}_start`, start || '');
                url.searchParams.set(`filter_value_${filterIndex}_end`, end || '');
                url.searchParams.set(`filter_value_${filterIndex}`, start || '');
            } else {
                url.searchParams.set(`filter_value_${filterIndex}`, value);
            }
            hasFilters = true;
            filtersData.push({
                field: field,
                op: op,
                value: value
            });
            filterIndex++;
        }
    }
    if (hasFilters) {
        localStorage.setItem('tables_filters', JSON.stringify(filtersData));
    } else {
        localStorage.removeItem('tables_filters');
    }
    window.location.href = url.toString();
    updateActiveNotices();
}

function clearFilters() {
    const filterFieldsContainer = document.getElementById('filterFields');
    if (filterFieldsContainer) {
        filterFieldsContainer.innerHTML = '';
        addFilterField();
    }
    localStorage.removeItem('tables_filters');
    sessionStorage.setItem('clearing_tables_filters', 'true');
    refreshTablesTable();
}

function restoreFilters() {
    sessionStorage.removeItem('clearing_tables_filters');
    const savedFilters = localStorage.getItem('tables_filters');
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
            localStorage.removeItem('tables_filters');
        }
    }
    const isClearing = sessionStorage.getItem('clearing_tables_filters');
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
            localStorage.setItem('tables_filters', JSON.stringify(filtersData));
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

function updateFilterOperators(index) {
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
            opSelect.value = currentOp;
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
    }
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
    if (selectedField === 'created_at' || selectedField === 'updated_at') {
        const valueContainer = row.querySelector('.col-md-3:nth-child(3)');
        if (!valueContainer) {
            return;
        }
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
                if (currentValue && currentValue.includes('|')) {
                    const [start] = currentValue.split('|');
                    newValueInput.value = start || '';
                } else if (currentValue) {
                    newValueInput.value = currentValue;
                }
            }
        }
    } else if (selectedField === 'id' || selectedField === 'alarms_count') {
        const valueInput = row.querySelector('.filter-value');
        if (valueInput) {
            if (['gt', 'lt', 'gte', 'lte', 'exact'].includes(selectedOp)) {
                valueInput.type = 'number';
                valueInput.placeholder = 'Число';
            } else {
                valueInput.type = 'text';
                valueInput.placeholder = 'Значение';
            }
        }
    } else {
        const valueInput = row.querySelector('.filter-value');
        if (valueInput) {
            valueInput.type = 'text';
            valueInput.placeholder = 'Значение';
        }
    }
}

function addFilterField(index = null, fieldValue = '', operatorValue = '', valueValue = '') {
    const filterFields = document.getElementById('filterFields');
    if (!filterFields) {
        console.error('Контейнер filterFields не найден!');
        return;
    }
    const currentCount = filterFields.querySelectorAll('.filter-row').length;
    const idx = index !== null ? index : currentCount;
    const row = document.createElement('div');
    row.className = 'row mb-2 filter-row';
    row.innerHTML = `
        <div class="col-md-3 mb-1">
            <select name="filter_field_${idx}" class="form-select form-select-sm filter-field" onchange="updateFilterOperators(${idx})">
                <option value="">Выберите поле</option>
                <option value="id" ${fieldValue === 'id' ? 'selected' : ''}>ID</option>
                <option value="name" ${fieldValue === 'name' ? 'selected' : ''}>Название</option>
                <option value="description" ${fieldValue === 'description' ? 'selected' : ''}>Описание</option>
                <option value="alarms_count" ${fieldValue === 'alarms_count' ? 'selected' : ''}>Количество аварий</option>
                <option value="created_at" ${fieldValue === 'created_at' ? 'selected' : ''}>Дата создания</option>
                <option value="updated_at" ${fieldValue === 'updated_at' ? 'selected' : ''}>Дата обновления</option>
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
                for (let i = 0; i < opSelect.options.length; i++) {
                    if (opSelect.options[i].value === operatorValue) {
                        opSelect.selectedIndex = i;
                        break;
                    }
                }
            }
        }
        // Если есть значение, устанавливаем его
        if (valueValue) {
            if (operatorValue === 'range' && (fieldValue === 'created_at' || fieldValue === 'updated_at')) {
                // Для диапазона дат разбираем значение
                const parts = valueValue.split('|');
                if (parts.length === 2) {
                    setTimeout(() => {
                        const startInput = row.querySelector(`input[name=\"filter_value_${idx}_start\"]`);
                        const endInput = row.querySelector(`input[name=\"filter_value_${idx}_end\"]`);
                        if (startInput) startInput.value = parts[0];
                        if (endInput) endInput.value = parts[1];
                    }, 0);
                }
            } else {
                const valueInput = row.querySelector('.filter-value');
                if (valueInput) valueInput.value = valueValue;
            }
        }
        setTimeout(() => updateFilterValueType(idx), 0);
    }
    updateActiveNotices();
}

function updateActiveNotices() {
    const sortActiveNotice = document.getElementById('sortActiveNotice');
    let sortActive = false;
    document.querySelectorAll('.sort-field').forEach(f => { if (f.value) sortActive = true; });
    if (sortActiveNotice) {
        sortActiveNotice.style.display = sortActive ? 'inline-block' : 'none';
    }
    const filtersActiveNotice = document.getElementById('filtersActiveNotice');
    let filtersActive = false;
    const urlParams = new URLSearchParams(window.location.search);
    const hasUrlFilters = Array.from(urlParams.keys()).some(key => key.startsWith('filter_field_'));
    document.querySelectorAll('.filter-row').forEach(row => {
        const field = row.querySelector('.filter-field');
        const op = row.querySelector('.filter-op');
        const val = row.querySelector('.filter-value');
        if (field && field.value && op && op.value && val && val.value) filtersActive = true;
    });
    if (filtersActiveNotice) {
        filtersActiveNotice.style.display = (filtersActive || hasUrlFilters) ? 'inline-block' : 'none';
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
        updateActiveNotices();
    }
} 