/**
 * Универсальный AG Grid компонент для страниц tables и alarms
 * Обеспечивает одинаковый функционал на обеих страницах
 */

// Глобальные настройки AG Grid
const AG_GRID_COMMON_CONFIG = {
    // Основные настройки
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 100,
        maxWidth: 400
    },

    // Пагинация
    pagination: true,
    paginationPageSize: 20,
    paginationPageSizeSelector: [10, 20, 50, 100],

    // Сортировка
    multiSortKey: 'ctrl',

    // Выбор строк
    rowSelection: 'multiple',

    // Экспорт
    enableRangeSelection: true,

    // Производительность
    animateRows: true,

    // Темы
    theme: 'ag-theme-alpine'
};

/**
 * Создает универсальную конфигурацию AG Grid
 * @param {string} pageType - тип страницы ('tables' или 'alarms')
 * @param {Array} columnDefs - определения колонок
 * @param {Array} rowData - данные строк
 * @returns {Object} конфигурация AG Grid
 */
function createGridConfig(pageType, columnDefs, rowData) {
    return {
        ...AG_GRID_COMMON_CONFIG,
        columnDefs: columnDefs,
        rowData: rowData,

        // События
        onGridReady: function (params) {
            // Автоматически подгоняем размер колонок под содержимое
            params.api.sizeColumnsToFit();

            // Загружаем сохраненные настройки
            loadGridSettings(pageType);

            // Инициализируем кнопки экспорта
            initExportButtons(pageType);
        },

        onSortChanged: function (event) {
            saveGridSettings(pageType);
        },

        onFilterChanged: function (event) {
            saveGridSettings(pageType);
        },

        onColumnMoved: function (event) {
            saveGridSettings(pageType);
        },

        onColumnResized: function (event) {
            saveGridSettings(pageType);
        },

        onColumnPinned: function (event) {
            saveGridSettings(pageType);
        }
    };
}

/**
 * Сохраняет настройки таблицы в localStorage
 * @param {string} pageType - тип страницы
 */
function saveGridSettings(pageType) {
    if (!window.gridApi) return;

    const settings = {
        columnState: window.gridApi.getColumnState(),
        sortModel: window.gridApi.getSortModel(),
        filterModel: window.gridApi.getFilterModel(),
        pinnedColumns: window.gridApi.getColumnDefs()
            .filter(col => col.pinned)
            .map(col => col.field)
    };

    localStorage.setItem(`${pageType}GridSettings`, JSON.stringify(settings));
}

/**
 * Загружает настройки таблицы из localStorage
 * @param {string} pageType - тип страницы
 */
function loadGridSettings(pageType) {
    if (!window.gridApi) return;

    const saved = localStorage.getItem(`${pageType}GridSettings`);
    if (saved) {
        try {
            const settings = JSON.parse(saved);

            if (settings.columnState) {
                window.gridApi.applyColumnState({
                    state: settings.columnState,
                    applyOrder: true
                });
            }

            if (settings.sortModel) {
                window.gridApi.setSortModel(settings.sortModel);
            }

            if (settings.filterModel) {
                window.gridApi.setFilterModel(settings.filterModel);
            }
        } catch (error) {
            console.error('Ошибка загрузки настроек:', error);
        }
    }
}

/**
 * Инициализирует кнопки экспорта
 * @param {string} pageType - тип страницы
 */
function initExportButtons(pageType) {
    const header = document.querySelector('.btn-toolbar');
    if (!header) return;

    // Проверяем, есть ли уже кнопки экспорта
    if (document.querySelector('.export-buttons')) return;

    const exportGroup = document.createElement('div');
    exportGroup.className = 'btn-group me-2 export-buttons';
    exportGroup.innerHTML = `
        <button type="button" class="btn btn-outline-success dropdown-toggle" data-bs-toggle="dropdown">
            <i class="bi bi-download"></i> Экспорт
        </button>
        <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#" onclick="exportToExcel('${pageType}')">
                <i class="bi bi-file-earmark-excel"></i> Excel
            </a></li>
            <li><a class="dropdown-item" href="#" onclick="exportToCsv('${pageType}')">
                <i class="bi bi-file-earmark-text"></i> CSV
            </a></li>
            <li><a class="dropdown-item" href="#" onclick="exportToPdf('${pageType}')">
                <i class="bi bi-file-earmark-pdf"></i> PDF
            </a></li>
        </ul>
    `;
    header.insertBefore(exportGroup, header.firstChild);
}

/**
 * Экспорт в Excel
 * @param {string} pageType - тип страницы
 */
function exportToExcel(pageType) {
    if (!window.gridApi) return;

    const fileName = `${pageType}_export_${new Date().toISOString().split('T')[0]}.xlsx`;
    window.gridApi.exportDataAsExcel({
        fileName: fileName,
        sheetName: pageType === 'tables' ? 'Таблицы тревог' : 'Тревоги'
    });
}

/**
 * Экспорт в CSV
 * @param {string} pageType - тип страницы
 */
function exportToCsv(pageType) {
    if (!window.gridApi) return;

    const fileName = `${pageType}_export_${new Date().toISOString().split('T')[0]}.csv`;
    window.gridApi.exportDataAsCsv({
        fileName: fileName
    });
}

/**
 * Экспорт в PDF
 * @param {string} pageType - тип страницы
 */
function exportToPdf(pageType) {
    if (!window.gridApi) return;

    const fileName = `${pageType}_export_${new Date().toISOString().split('T')[0]}.pdf`;
    window.gridApi.exportDataAsPdf({
        fileName: fileName,
        title: pageType === 'tables' ? 'Таблицы тревог' : 'Тревоги'
    });
}

/**
 * Сброс настроек таблицы
 * @param {string} pageType - тип страницы
 */
function resetGridSettings(pageType) {
    localStorage.removeItem(`${pageType}GridSettings`);

    if (window.gridApi) {
        // Сбрасываем сортировку
        window.gridApi.setSortModel([]);

        // Сбрасываем фильтры
        window.gridApi.setFilterModel(null);

        // Сбрасываем порядок колонок
        const defaultColumnState = window.gridApi.getColumnDefs().map((col, index) => ({
            colId: col.field,
            width: col.width,
            hide: false,
            pinned: col.pinned || null,
            sort: null,
            sortIndex: null
        }));

        window.gridApi.applyColumnState({
            state: defaultColumnState,
            applyOrder: true
        });
    }

    showNotification('Настройки сброшены к умолчаниям', 'info');
}

/**
 * Показывает уведомление
 * @param {string} message - сообщение
 * @param {string} type - тип уведомления
 */
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

/**
 * Инициализирует AG Grid
 * @param {string} containerId - ID контейнера
 * @param {Object} gridOptions - опции AG Grid
 */
function initAgGrid(containerId, gridOptions) {
    console.log('initAgGrid вызвана с:', { containerId, gridOptions });

    const gridDiv = document.querySelector(`#${containerId}`);
    if (!gridDiv) {
        console.error(`Контейнер #${containerId} не найден`);
        return;
    }

    console.log('Контейнер найден:', gridDiv);
    console.log('agGrid доступен:', typeof agGrid);

    try {
        // Сохраняем API в глобальной переменной
        window.gridApi = new agGrid.Grid(gridDiv, gridOptions);
        console.log('AG Grid создан успешно:', window.gridApi);

        return window.gridApi;
    } catch (error) {
        console.error('Ошибка создания AG Grid:', error);
        throw error;
    }
}

/**
 * Общие стили для AG Grid
 */
const AG_GRID_STYLES = `
<style>
    /* Контейнер для AG Grid */
    .ag-grid-container {
        height: 600px;
        width: 100%;
    }
    
    /* Стили для кнопок действий */
    .action-buttons {
        display: flex;
        gap: 5px;
    }
    
    .action-buttons .btn {
        padding: 2px 6px;
        font-size: 12px;
    }
    
    /* Стили для счетчиков */
    .count-badge {
        font-weight: bold;
        color: #007bff;
    }
    
    /* Стили для описания */
    .description-cell {
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* Стили для дат */
    .date-cell {
        font-size: 12px;
        color: #666;
    }
    
    /* Стили для приоритетов */
    .priority-high {
        color: #dc3545;
        font-weight: bold;
    }
    
    .priority-medium {
        color: #fd7e14;
        font-weight: bold;
    }
    
    .priority-low {
        color: #28a745;
        font-weight: bold;
    }
    
    /* Стили для статусов */
    .status-active {
        color: #28a745;
    }
    
    .status-inactive {
        color: #6c757d;
    }
</style>
`;

// Добавляем стили в head при загрузке
document.addEventListener('DOMContentLoaded', function () {
    if (!document.querySelector('#ag-grid-styles')) {
        const styleElement = document.createElement('div');
        styleElement.id = 'ag-grid-styles';
        styleElement.innerHTML = AG_GRID_STYLES;
        document.head.appendChild(styleElement);
    }
}); 