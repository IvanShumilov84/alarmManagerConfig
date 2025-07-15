// Универсальный модуль сортировки для страниц alarms и tables
// Использование: <div id="sortFields" data-sort-fields='[{...}]' data-storage-key="alarmsSortFields"></div>

(function () {
    // Получаем параметры из data-атрибутов
    function getConfig() {
        const container = document.getElementById('sortFields');
        if (!container) return null;
        let fields = [];
        let storageKey = 'sortFields';
        try {
            fields = JSON.parse(container.dataset.sortFields || '[]');
        } catch { fields = []; }
        if (container.dataset.storageKey) storageKey = container.dataset.storageKey;
        return { fields, storageKey, container };
    }

    function renderSortFields(savedValues = null) {
        const config = getConfig();
        if (!config) return;
        const { fields, storageKey, container } = config;
        container.innerHTML = '';
        let values = savedValues;
        if (!values) {
            // Восстанавливаем из localStorage или из DOM
            const ls = localStorage.getItem(storageKey);
            if (ls) {
                try {
                    values = JSON.parse(ls);
                    if (!Array.isArray(values) || values.length === 0 || !values.some(s => s.field && s.field.trim() !== '')) {
                        values = [];
                    }
                } catch { values = []; }
            } else {
                values = [];
                const currentFields = container.querySelectorAll('.sort-field');
                const currentOrders = container.querySelectorAll('.sort-order');
                for (let i = 0; i < currentFields.length; i++) {
                    values.push({
                        field: currentFields[i].value,
                        order: currentOrders[i].value
                    });
                }
            }
        }
        if (!values || values.length === 0) {
            values = [{ field: '', order: 'asc' }];
        }
        for (let i = 0; i < values.length; i++) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'col-md-3 mb-2';
            let options = `<option value="">Выберите поле</option>`;
            for (const f of fields) {
                options += `<option value="${f.value}" ${values[i].field === f.value ? 'selected' : ''}>${f.label}</option>`;
            }
            fieldDiv.innerHTML = `
                <select name="sort_${i}" class="form-select form-select-sm sort-field">${options}</select>
            `;
            const orderDiv = document.createElement('div');
            orderDiv.className = 'col-md-3 mb-2';
            orderDiv.innerHTML = `
                <select name="order_${i}" class="form-select form-select-sm sort-order">
                    <option value="asc" ${values[i].order === 'asc' ? 'selected' : ''}>По возрастанию</option>
                    <option value="desc" ${values[i].order === 'desc' ? 'selected' : ''}>По убыванию</option>
                </select>
            `;
            const removeBtn = document.createElement('div');
            removeBtn.className = 'col-md-3 mb-2';
            removeBtn.innerHTML = `
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="window.sortModule.removeSortField(${i})" title="Удалить сортировку">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            const spacer = document.createElement('div');
            spacer.className = 'col-md-3 mb-2';
            container.appendChild(fieldDiv);
            container.appendChild(orderDiv);
            container.appendChild(removeBtn);
            container.appendChild(spacer);
        }
        // Кнопки управления
        const btnGroup = document.createElement('div');
        btnGroup.className = 'd-flex mb-2';
        const clearBtn = document.createElement('div');
        clearBtn.innerHTML = `
            <button type="button" class="btn btn-sm btn-outline-danger me-2" id="clearSortBtn">
                <i class="bi bi-x"></i> Очистить всю сортировку
            </button>
        `;
        const addBtn = document.createElement('div');
        addBtn.innerHTML = `
            <button type="button" class="btn btn-sm btn-outline-success me-2" id="addSortBtn">
                <i class="bi bi-plus"></i> Добавить
            </button>
        `;
        const applyBtn = document.createElement('div');
        applyBtn.innerHTML = `
            <button type="button" class="btn btn-sm btn-outline-primary" id="applySortBtn">
                <i class="bi bi-check"></i> Применить сортировку
            </button>
        `;
        btnGroup.appendChild(clearBtn);
        btnGroup.appendChild(addBtn);
        btnGroup.appendChild(applyBtn);
        container.appendChild(btnGroup);
        if (document.getElementById('currentSortDisplay')) {
            updateSortDisplay();
        }
        updateActiveNotices();
    }

    function addSortField() {
        const config = getConfig();
        if (!config) return;
        const { container } = config;
        const currentFields = container.querySelectorAll('.sort-field');
        const currentOrders = container.querySelectorAll('.sort-order');
        const savedValues = [];
        for (let i = 0; i < currentFields.length; i++) {
            savedValues.push({
                field: currentFields[i].value,
                order: currentOrders[i].value
            });
        }
        savedValues.push({ field: '', order: 'asc' });
        renderSortFields(savedValues);
        updateActiveNotices();
    }

    function removeSortField(index) {
        const config = getConfig();
        if (!config) return;
        const { container, storageKey, fields } = config;
        const currentFields = container.querySelectorAll('.sort-field');
        const currentOrders = container.querySelectorAll('.sort-order');
        const savedValues = [];
        for (let i = 0; i < currentFields.length; i++) {
            savedValues.push({
                field: currentFields[i].value,
                order: currentOrders[i].value
            });
        }
        savedValues.splice(index, 1);
        if (savedValues.length === 0) {
            localStorage.removeItem(storageKey);
            const url = new URL(window.location.href);
            for (const key of Array.from(url.searchParams.keys())) {
                if (key.startsWith('sort_') || key.startsWith('order_')) {
                    url.searchParams.delete(key);
                }
            }
            url.searchParams.set('sort_0', fields[0]?.value || 'id');
            url.searchParams.set('order_0', 'asc');
            window.location.href = url.pathname + '?' + url.searchParams.toString();
            return;
        }
        // --- Новое: сразу применяем сортировку ---
        localStorage.setItem(storageKey, JSON.stringify(savedValues));
        const url = new URL(window.location.href);
        for (const key of Array.from(url.searchParams.keys())) {
            if (key.startsWith('sort_') || key.startsWith('order_')) {
                url.searchParams.delete(key);
            }
        }
        let sortCount = 0;
        for (let i = 0; i < savedValues.length; i++) {
            const field = savedValues[i].field;
            const order = savedValues[i].order || 'asc';
            if (field) {
                url.searchParams.set(`sort_${sortCount}`, field);
                url.searchParams.set(`order_${sortCount}`, order);
                sortCount++;
            }
        }
        window.location.href = url.pathname + '?' + url.searchParams.toString();
    }

    function clearSort() {
        const config = getConfig();
        if (!config) return;
        const { storageKey, fields } = config;
        localStorage.removeItem(storageKey);
        const url = new URL(window.location.href);
        for (const key of Array.from(url.searchParams.keys())) {
            if (key.startsWith('sort_') || key.startsWith('order_')) {
                url.searchParams.delete(key);
            }
        }
        url.searchParams.set('sort_0', fields[0]?.value || 'id');
        url.searchParams.set('order_0', 'asc');
        window.location.href = url.pathname + '?' + url.searchParams.toString();
    }

    function updateSortDisplay() {
        const config = getConfig();
        if (!config) return;
        const { container, fields } = config;
        const currentFields = container.querySelectorAll('.sort-field');
        const currentOrders = container.querySelectorAll('.sort-order');
        const currentSortDisplay = document.getElementById('currentSortDisplay');
        if (!currentSortDisplay) return;
        let displayText = '';
        for (let i = 0; i < currentFields.length; i++) {
            const field = currentFields[i].value;
            const order = currentOrders[i] ? currentOrders[i].value : 'asc';
            if (field) {
                let fieldName = fields.find(f => f.value === field)?.label || field;
                let orderSymbol = order === 'asc' ? '↑' : '↓';
                displayText += `${fieldName} ${orderSymbol}, `;
            }
        }
        currentSortDisplay.textContent = displayText ? displayText.slice(0, -2) : 'Не выбрана';
    }

    function toggleSortSettings() {
        const sortSettingsBody = document.getElementById('sortSettingsBody');
        const sortToggleIcon = document.getElementById('sortToggleIcon');
        if (!sortSettingsBody || !sortToggleIcon) return;
        if (sortSettingsBody.style.display === 'none' || sortSettingsBody.style.display === '') {
            sortSettingsBody.style.display = 'block';
            sortToggleIcon.className = 'bi bi-chevron-down';
            localStorage.setItem('sortSettingsExpanded', 'true');
        } else {
            sortSettingsBody.style.display = 'none';
            sortToggleIcon.className = 'bi bi-chevron-right';
            localStorage.setItem('sortSettingsExpanded', 'false');
        }
        const sortActiveNotice = document.getElementById('sortActiveNotice');
        if (sortSettingsBody.style.display === 'none' || sortSettingsBody.style.display === '') {
            if (sortActiveNotice) sortActiveNotice.style.display = 'none';
        } else {
            let active = false;
            document.querySelectorAll('.sort-field').forEach(f => { if (f.value) active = true; });
            if (sortActiveNotice) sortActiveNotice.style.display = active ? 'block' : 'none';
        }
        updateActiveNotices();
    }

    function updateActiveNotices() {
        // Показывать бейдж только если сортировка реально применена (есть параметры сортировки в URL)
        const sortActiveNotice = document.getElementById('sortActiveNotice');
        if (!sortActiveNotice) return;
        const url = new URL(window.location.href);
        let hasSortParams = false;
        for (const key of url.searchParams.keys()) {
            if (key.startsWith('sort_') && url.searchParams.get(key)) {
                hasSortParams = true;
                break;
            }
        }
        sortActiveNotice.style.display = hasSortParams ? 'block' : 'none';
    }

    // === Универсальная инициализация сортировки ===
    document.addEventListener('DOMContentLoaded', () => {
        // Восстановление состояния спойлера сортировки
        const sortSettingsBody = document.getElementById('sortSettingsBody');
        const sortToggleIcon = document.getElementById('sortToggleIcon');
        let sortLSKey = 'alarmsSortSettingsExpanded';
        if (window.location.pathname.includes('/tables/')) {
            sortLSKey = 'tablesSortSettingsExpanded';
        }
        if (localStorage.getItem(sortLSKey) === 'false') {
            if (sortSettingsBody && sortToggleIcon) {
                sortSettingsBody.style.display = 'none';
                sortToggleIcon.className = 'bi bi-chevron-right';
            }
        } else {
            if (sortSettingsBody && sortToggleIcon) {
                sortSettingsBody.style.display = 'block';
                sortToggleIcon.className = 'bi bi-chevron-down';
            }
        }
        // --- Автоматическое применение сортировки при входе (универсально) ---
        const url = new URL(window.location.href);
        let hasSortParams = false;
        for (const key of url.searchParams.keys()) {
            if (key.startsWith('sort_')) {
                hasSortParams = true;
                break;
            }
        }
        // Определяем storageKey по странице
        let storageKey = 'sortFields';
        if (window.location.pathname.includes('/alarms/')) {
            storageKey = 'alarmsSortFields';
        } else if (window.location.pathname.includes('/tables/')) {
            storageKey = 'tablesSortFields';
        }
        if (!hasSortParams) {
            const savedSort = localStorage.getItem(storageKey);
            if (savedSort) {
                try {
                    const sortArr = JSON.parse(savedSort);
                    if (Array.isArray(sortArr) && sortArr.length > 0 && sortArr.some(s => s.field && s.field.trim() !== '')) {
                        sortArr.forEach((s, i) => {
                            if (s.field && s.field.trim() !== '') {
                                url.searchParams.set(`sort_${i}`, s.field);
                                url.searchParams.set(`order_${i}`, s.order || 'asc');
                            }
                        });
                        window.location.replace(url.pathname + '?' + url.searchParams.toString());
                        return;
                    }
                } catch (e) { }
            }
        }
        renderSortFields();
        // Восстановление фильтров и прочего — вне этого модуля
        // Обработчики кнопок
        document.addEventListener('click', function (event) {
            // Универсальный поиск по id через closest для вложенных элементов
            const clearBtn = event.target.closest('#clearSortBtn');
            const applyBtn = event.target.closest('#applySortBtn');
            const addBtn = event.target.closest('#addSortBtn');
            if (applyBtn) {
                event.preventDefault();
                const container = document.getElementById('sortFields');
                const sortFields = container.querySelectorAll('.sort-field');
                const sortOrders = container.querySelectorAll('.sort-order');
                const url = new URL(window.location.href);
                for (const key of Array.from(url.searchParams.keys())) {
                    if (key.startsWith('sort_') || key.startsWith('order_')) {
                        url.searchParams.delete(key);
                    }
                }
                let sortCount = 0;
                const sortToSave = [];
                for (let i = 0; i < sortFields.length; i++) {
                    const field = sortFields[i].value;
                    const order = sortOrders[i] ? sortOrders[i].value : 'asc';
                    if (field) {
                        url.searchParams.set(`sort_${sortCount}`, field);
                        url.searchParams.set(`order_${sortCount}`, order);
                        sortToSave.push({ field, order });
                        sortCount++;
                    }
                }
                localStorage.setItem(storageKey, JSON.stringify(sortToSave));
                window.location.href = url.pathname + '?' + url.searchParams.toString();
            }
            if (addBtn) {
                event.preventDefault();
                addSortField();
            }
            if (clearBtn) {
                event.preventDefault();
                console.log('Клик по кнопке Очистить сортировку!');
                clearSort();
            }
        });
    });

    // Экспортируем функции для inline-обработчиков
    window.sortModule = {
        renderSortFields,
        addSortField,
        removeSortField,
        clearSort,
        updateSortDisplay,
        toggleSortSettings
    };
})();

// Глобальная функция для inline-обработчиков
function toggleSortSettings() {
    const sortSettingsBody = document.getElementById('sortSettingsBody');
    const sortToggleIcon = document.getElementById('sortToggleIcon');
    if (!sortSettingsBody || !sortToggleIcon) return;

    if (sortSettingsBody.style.display === 'none' || sortSettingsBody.style.display === '') {
        sortSettingsBody.style.display = 'block';
        sortToggleIcon.className = 'bi bi-chevron-down';
        // Определяем ключ localStorage по странице
        let sortLSKey = 'alarmsSortSettingsExpanded';
        if (window.location.pathname.includes('/tables/')) {
            sortLSKey = 'tablesSortSettingsExpanded';
        }
        localStorage.setItem(sortLSKey, 'true');
    } else {
        sortSettingsBody.style.display = 'none';
        sortToggleIcon.className = 'bi bi-chevron-right';
        // Определяем ключ localStorage по странице
        let sortLSKey = 'alarmsSortSettingsExpanded';
        if (window.location.pathname.includes('/tables/')) {
            sortLSKey = 'tablesSortSettingsExpanded';
        }
        localStorage.setItem(sortLSKey, 'false');
    }

    const sortActiveNotice = document.getElementById('sortActiveNotice');
    if (sortSettingsBody.style.display === 'none' || sortSettingsBody.style.display === '') {
        if (sortActiveNotice) sortActiveNotice.style.display = 'none';
    } else {
        let active = false;
        document.querySelectorAll('.sort-field').forEach(f => { if (f.value) active = true; });
        if (sortActiveNotice) sortActiveNotice.style.display = active ? 'block' : 'none';
    }
} 