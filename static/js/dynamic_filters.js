// Динамические выпадающие списки для фильтров
// Загружает справочники из API и создает select-элементы

// Кэш для загруженных справочников
const filterCache = {};

// Маппинг полей к API-эндпоинтам
const FIELD_API_MAPPING = {
    'alarm_class': '/api/alarm-classes/',
    'logic': '/api/logics/',
    'confirm_method': '/api/confirm-methods/',
    'limit_type': '/api/limit-types/',
    'limit_config_type': '/api/limit-config-types/'
};

/**
 * Загружает справочник с сервера
 * @param {string} fieldName - имя поля фильтра
 * @returns {Promise<Array>} - массив объектов с id и verbose_name_ru
 */
async function loadFilterData(fieldName) {
    const apiUrl = FIELD_API_MAPPING[fieldName];
    if (!apiUrl) {
        console.warn(`Нет API для поля: ${fieldName}`);
        return [];
    }

    // Проверяем кэш
    if (filterCache[fieldName]) {
        return filterCache[fieldName];
    }

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Кэшируем результат
        filterCache[fieldName] = data;
        return data;
    } catch (error) {
        console.error(`Ошибка загрузки справочника для ${fieldName}:`, error);
        return [];
    }
}

/**
 * Создает select-элемент для поля фильтра
 * @param {string} fieldName - имя поля
 * @param {string} selectedValue - выбранное значение
 * @param {number} index - индекс фильтра
 * @returns {HTMLSelectElement} - созданный select-элемент
 */
function createFilterSelect(fieldName, selectedValue = '', index = 0) {
    const select = document.createElement('select');
    select.className = 'form-select form-select-sm filter-value';
    select.name = `filter_value_${index}`;
    select.setAttribute('data-field', fieldName);

    // Добавляем опцию по умолчанию
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Выберите значение...';
    select.appendChild(defaultOption);

    // Загружаем данные и заполняем select
    loadFilterData(fieldName).then(data => {
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.verbose_name_ru; // Используем русское название как значение
            option.textContent = item.verbose_name_ru;
            if (item.verbose_name_ru === selectedValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });

    return select;
}

/**
 * Проверяет, нужно ли создавать select для поля
 * @param {string} fieldName - имя поля
 * @returns {boolean} - true если поле поддерживает выпадающий список
 */
function shouldUseSelect(fieldName) {
    return fieldName in FIELD_API_MAPPING;
}

/**
 * Заменяет input на select для полей с выпадающими списками
 * @param {HTMLElement} row - строка фильтра
 * @param {string} fieldName - имя поля
 * @param {string} selectedValue - выбранное значение
 * @param {number} index - индекс фильтра
 */
function replaceInputWithSelect(row, fieldName, selectedValue, index) {
    const valueContainer = row.querySelector('.col-md-3:nth-child(3)');
    if (!valueContainer) return;

    // Удаляем старый input
    const oldInput = valueContainer.querySelector('.filter-value');
    if (oldInput) {
        oldInput.remove();
    }

    // Создаем и добавляем новый select
    const select = createFilterSelect(fieldName, selectedValue, index);
    valueContainer.appendChild(select);
}

/**
 * Инициализирует динамические фильтры на странице
 */
function initDynamicFilters() {
    console.log('Инициализация динамических фильтров...');

    // Обрабатываем существующие фильтры
    const filterRows = document.querySelectorAll('.filter-row');
    filterRows.forEach((row, index) => {
        const fieldSelect = row.querySelector('.filter-field');
        if (fieldSelect && shouldUseSelect(fieldSelect.value)) {
            const valueInput = row.querySelector('.filter-value');
            const currentValue = valueInput ? valueInput.value : '';
            replaceInputWithSelect(row, fieldSelect.value, currentValue, index);
        }
    });

    // Добавляем обработчик для изменения поля фильтра
    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('filter-field')) {
            const row = event.target.closest('.filter-row');
            const fieldName = event.target.value;
            const index = Array.from(document.querySelectorAll('.filter-row')).indexOf(row);

            if (shouldUseSelect(fieldName)) {
                replaceInputWithSelect(row, fieldName, '', index);
            } else {
                // Возвращаем обычный input для полей без выпадающего списка
                const valueContainer = row.querySelector('.col-md-3:nth-child(3)');
                if (valueContainer) {
                    const oldSelect = valueContainer.querySelector('.filter-value');
                    if (oldSelect && oldSelect.tagName === 'SELECT') {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.className = 'form-control form-control-sm filter-value';
                        input.name = `filter_value_${index}`;
                        input.placeholder = 'Значение';
                        oldSelect.replaceWith(input);
                    }
                }
            }
        }
    });
}

// Инициализируем при загрузке страницы
document.addEventListener('DOMContentLoaded', initDynamicFilters); 