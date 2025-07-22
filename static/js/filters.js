// Универсальный JS-модуль фильтрации для таблиц аварий

// Глобальные переменные
let filterFields = [];
let sortFields = [];
let currentPageType = 'alarms'; // или 'tables'

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Определяем тип страницы
    currentPageType = window.location.pathname.includes('tables') ? 'tables' : 'alarms';

    // Загружаем поля фильтров и сортировки
    loadFilterFields();
    loadSortFields();

    // Восстанавливаем сохраненные фильтры и сортировки
    restoreFilters();
    restoreSorts();

    // Обработчики событий
    setupEventListeners();

    // Обновляем счетчики
    updateCounters();
});

// Настройка обработчиков событий
function setupEventListeners() {
    // Обработчик для кнопки применения фильтров
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function (event) {
            event.preventDefault();
            applyFilters();
        });
    }

    // Обработчик для кнопки применения сортировки
    const applySortsBtn = document.getElementById('applySortsBtn');
    if (applySortsBtn) {
        applySortsBtn.addEventListener('click', function (event) {
            event.preventDefault();
            applySorts();
        });
    }

    // Обработчик изменения количества записей на странице
    const recordsPerPage = document.getElementById('recordsPerPage');
    if (recordsPerPage) {
        recordsPerPage.addEventListener('change', function () {
            saveCurrentSettings();
        });
    }
}

// Загрузка полей фильтров
async function loadFilterFields() {
    try {
        const response = await fetch(`/api/filter-fields/?type=${currentPageType}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        filterFields = data.fields;
        console.log('Filter fields loaded:', filterFields);
    } catch (error) {
        console.error('Error loading filter fields:', error);
        showNotification('Ошибка загрузки полей фильтров', 'danger');
    }
}

// Загрузка полей сортировки
async function loadSortFields() {
    try {
        const response = await fetch(`/api/sort-fields/?type=${currentPageType}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        sortFields = data.fields;
        console.log('Sort fields loaded:', sortFields);
    } catch (error) {
        console.error('Error loading sort fields:', error);
        showNotification('Ошибка загрузки полей сортировки', 'danger');
    }
}

// Добавление поля фильтра
function addFilterField() {
    const filterFieldsContainer = document.getElementById('filterFields');
    const filterIndex = filterFieldsContainer.children.length;

    const filterRow = document.createElement('div');
    filterRow.className = 'col-md-12 mb-2 filter-row';
    filterRow.innerHTML = `
        <div class="row g-2">
            <div class="col-md-3">
                <select class="form-select form-select-sm" name="filter_field_${filterIndex}" onchange="updateFilterValue(${filterIndex})">
                    <option value="">Выберите поле</option>
                    ${filterFields.map(field => `<option value="${field.value}">${field.label}</option>`).join('')}
                </select>
            </div>
            <div class="col-md-2">
                <select class="form-select form-select-sm" name="filter_operator_${filterIndex}">
            <option value="exact">Равно</option>
                    <option value="icontains">Содержит</option>
            <option value="startswith">Начинается с</option>
            <option value="endswith">Заканчивается на</option>
                    <option value="gt">Больше</option>
                    <option value="gte">Больше или равно</option>
                    <option value="lt">Меньше</option>
                    <option value="lte">Меньше или равно</option>
                    <option value="in">В списке</option>
                </select>
            </div>
            <div class="col-md-4">
                <input type="text" class="form-control form-control-sm" name="filter_value_${filterIndex}" placeholder="Значение">
                    </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFilterField(this)">
                    <i class="fas fa-trash"></i>
                </button>
                    </div>
                </div>
            `;

    filterFieldsContainer.appendChild(filterRow);
    updateCounters();
}

// Добавление поля сортировки
function addSortField() {
    const sortFieldsContainer = document.getElementById('sortFields');
    const sortIndex = sortFieldsContainer.children.length;

    const sortRow = document.createElement('div');
    sortRow.className = 'col-md-12 mb-2 sort-row';
    sortRow.innerHTML = `
        <div class="row g-2">
            <div class="col-md-4">
                <select class="form-select form-select-sm" name="sort_${sortIndex}">
                    <option value="">Выберите поле</option>
                    ${sortFields.map(field => `<option value="${field.value}">${field.label}</option>`).join('')}
            </select>
        </div>
            <div class="col-md-3">
                <select class="form-select form-select-sm" name="order_${sortIndex}">
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
            </select>
        </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeSortField(this)">
                    <i class="fas fa-trash"></i>
                </button>
        </div>
        </div>
    `;

    sortFieldsContainer.appendChild(sortRow);
    updateCounters();
}

// Удаление поля фильтра
function removeFilterField(button) {
    button.closest('.filter-row').remove();
    updateCounters();
    saveFilters();
}

// Удаление поля сортировки
function removeSortField(button) {
    button.closest('.sort-row').remove();
    updateCounters();
    saveSorts();
}

// Очистка всех фильтров
function clearAllFilters() {
    const filterFieldsContainer = document.getElementById('filterFields');
    filterFieldsContainer.innerHTML = '';
    updateCounters();
    saveFilters();
    showNotification('Все фильтры очищены', 'info');
}

// Очистка всей сортировки
function clearAllSorts() {
    const sortFieldsContainer = document.getElementById('sortFields');
    sortFieldsContainer.innerHTML = '';
    updateCounters();
    saveSorts();
    showNotification('Вся сортировка очищена', 'info');
}

// Применение фильтров
function applyFilters() {
    const form = document.getElementById('filterForm');
    if (form) {
        // Сохраняем фильтры перед отправкой
        saveFilters();
        form.submit();
    }
}

// Применение сортировки
function applySorts() {
    const form = document.getElementById('sortForm');
    if (form) {
        // Сохраняем сортировку перед отправкой
        saveSorts();
        form.submit();
    }
}

// Сохранение фильтров в localStorage
function saveFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        const formData = new FormData(filterForm);
        const filters = {};

        for (let [key, value] of formData.entries()) {
            if (value) {
                filters[key] = value;
            }
        }

        localStorage.setItem(`${currentPageType}Filters`, JSON.stringify(filters));
    }
}

// Сохранение сортировки в localStorage
function saveSorts() {
    const sortForm = document.getElementById('sortForm');
    if (sortForm) {
        const formData = new FormData(sortForm);
        const sorts = {};

        for (let [key, value] of formData.entries()) {
            if (value) {
                sorts[key] = value;
            }
        }

        localStorage.setItem(`${currentPageType}Sorts`, JSON.stringify(sorts));
    }
}

// Восстановление фильтров из localStorage
function restoreFilters() {
    const savedFilters = JSON.parse(localStorage.getItem(`${currentPageType}Filters`) || '{}');

    // Очищаем существующие фильтры
    const filterFieldsContainer = document.getElementById('filterFields');
    filterFieldsContainer.innerHTML = '';

    // Восстанавливаем фильтры
    let filterIndex = 0;
    for (let key in savedFilters) {
        if (key.startsWith('filter_field_')) {
            const fieldValue = savedFilters[key];
            const operatorValue = savedFilters[key.replace('filter_field_', 'filter_operator_')] || 'exact';
            const valueValue = savedFilters[key.replace('filter_field_', 'filter_value_')] || '';

            if (fieldValue) {
                addFilterField();
                const lastRow = filterFieldsContainer.lastElementChild;

                // Устанавливаем значения
                lastRow.querySelector(`[name="filter_field_${filterIndex}"]`).value = fieldValue;
                lastRow.querySelector(`[name="filter_operator_${filterIndex}"]`).value = operatorValue;
                lastRow.querySelector(`[name="filter_value_${filterIndex}"]`).value = valueValue;

                filterIndex++;
            }
        }
    }
}

// Восстановление сортировки из localStorage
function restoreSorts() {
    const savedSorts = JSON.parse(localStorage.getItem(`${currentPageType}Sorts`) || '{}');

    // Очищаем существующую сортировку
    const sortFieldsContainer = document.getElementById('sortFields');
    sortFieldsContainer.innerHTML = '';

    // Восстанавливаем сортировку
    let sortIndex = 0;
    for (let key in savedSorts) {
        if (key.startsWith('sort_')) {
            const fieldValue = savedSorts[key];
            const orderValue = savedSorts[key.replace('sort_', 'order_')] || 'asc';

            if (fieldValue) {
                addSortField();
                const lastRow = sortFieldsContainer.lastElementChild;

                // Устанавливаем значения
                lastRow.querySelector(`[name="sort_${sortIndex}"]`).value = fieldValue;
                lastRow.querySelector(`[name="order_${sortIndex}"]`).value = orderValue;

                sortIndex++;
            }
        }
    }
}

// Обновление счетчиков
function updateCounters() {
    // Счетчик активных фильтров
    const activeFilters = document.querySelectorAll('#filterFields .filter-row').length;
    const filtersCount = document.getElementById('activeFiltersCount');
    if (filtersCount) {
        if (activeFilters > 0) {
            filtersCount.textContent = activeFilters;
            filtersCount.style.display = 'inline';
        } else {
            filtersCount.style.display = 'none';
        }
    }

    // Счетчик активных сортировок
    const activeSorts = document.querySelectorAll('#sortFields .sort-row').length;
    const sortsCount = document.getElementById('activeSortsCount');
    if (sortsCount) {
        if (activeSorts > 0) {
            sortsCount.textContent = activeSorts;
            sortsCount.style.display = 'inline';
        } else {
            sortsCount.style.display = 'none';
        }
    }
}

// Уведомления
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
} 