/**
 * Управление темами
 */
class ThemeManager {
    constructor() {
        this.html = document.documentElement;
        this.themeIcon = document.getElementById('themeIcon');
        this.sidebarThemeIcon = document.getElementById('sidebarThemeIcon');
        this.themeText = document.getElementById('themeText');
        this.storageKey = 'theme';
        
        this.init();
    }
    
    init() {
        this.loadTheme();
        this.bindEvents();
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem(this.storageKey) || 'system';
        let currentTheme = savedTheme;
        let iconClass, themeLabel;
        
        if (savedTheme === 'system') {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                currentTheme = 'dark';
            } else {
                currentTheme = 'light';
            }
            iconClass = 'bi bi-laptop';
            themeLabel = 'Системная';
        } else if (savedTheme === 'dark') {
            iconClass = 'bi bi-moon-fill';
            themeLabel = 'Тёмная';
        } else {
            iconClass = 'bi bi-sun-fill';
            themeLabel = 'Светлая';
        }
        
        this.html.setAttribute('data-bs-theme', currentTheme);
        this.updateIcons(iconClass, themeLabel);
        
        // Слушаем изменения системной темы
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (localStorage.getItem(this.storageKey) === 'system') {
                    const newTheme = e.matches ? 'dark' : 'light';
                    this.html.setAttribute('data-bs-theme', newTheme);
                }
            });
        }
    }
    
    bindEvents() {
        // Обработчик для кнопки переключения темы
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggle());
        }
        
        // Обработчик для кнопки в сайдбаре
        const sidebarThemeToggle = document.querySelector('button[onclick="toggleTheme()"]');
        if (sidebarThemeToggle) {
            sidebarThemeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });
        }
    }
    
    toggle() {
        const savedTheme = localStorage.getItem(this.storageKey) || 'light';
        
        this.html.style.transition = 'all 0.3s ease';
        
        let newTheme, newSavedTheme, notificationMessage, iconClass, themeLabel;
        
        if (savedTheme === 'light') {
            newSavedTheme = 'dark';
            newTheme = 'dark';
            iconClass = 'bi bi-moon-fill';
            themeLabel = 'Тёмная';
            notificationMessage = 'Тёмная тема включена';
        } else if (savedTheme === 'dark') {
            newSavedTheme = 'system';
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                newTheme = 'dark';
            } else {
                newTheme = 'light';
            }
            iconClass = 'bi bi-laptop';
            themeLabel = 'Системная';
            notificationMessage = 'Системная тема включена';
        } else {
            newSavedTheme = 'light';
            newTheme = 'light';
            iconClass = 'bi bi-sun-fill';
            themeLabel = 'Светлая';
            notificationMessage = 'Светлая тема включена';
        }
        
        this.html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem(this.storageKey, newSavedTheme);
        this.updateIcons(iconClass, themeLabel);
        
        this.showNotification(notificationMessage);
        
        setTimeout(() => {
            this.html.style.transition = '';
        }, 300);
    }
    
    updateIcons(iconClass, themeLabel) {
        if (this.themeIcon) this.themeIcon.className = iconClass;
        if (this.sidebarThemeIcon) this.sidebarThemeIcon.className = iconClass;
        if (this.themeText) this.themeText.textContent = themeLabel;
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--card-bg);
            color: var(--text-color);
            padding: 8px 16px;
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
            z-index: 998;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            font-size: 0.9rem;
            max-width: 200px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 2000);
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Глобальная функция для совместимости
window.toggleTheme = function() {
    if (window.themeManager) {
        window.themeManager.toggle();
    }
}; 