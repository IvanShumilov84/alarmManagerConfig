/**
 * Управление сайдбаром
 */
class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.toggleIcon = document.getElementById('sidebarToggleIcon');
        this.toggleButton = document.getElementById('sidebarToggleBtn');
        this.titleText = document.querySelector('.sidebar-title-text');
        this.mainContent = document.getElementById('mainContent');
        this.storageKey = 'sidebarMinimized';
        
        this.init();
    }
    
    init() {
        this.loadState();
        this.bindEvents();
    }
    
    loadState() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.add('loaded');
        const isMinimized = localStorage.getItem(this.storageKey) === 'true';
        
        if (isMinimized) {
            this.minimize();
        } else {
            this.expand();
        }
    }
    
    bindEvents() {
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });
        }
    }
    
    toggle() {
        const isMinimized = this.sidebar.classList.contains('minimized');
        
        if (isMinimized) {
            this.expand();
        } else {
            this.minimize();
        }
    }
    
    minimize() {
        this.sidebar.classList.add('minimized');
        document.body.classList.add('sidebar-minimized');
        
        if (this.toggleIcon) {
            this.toggleIcon.className = 'bi bi-arrows-angle-expand';
        }
        if (this.toggleButton) {
            this.toggleButton.setAttribute('data-title', 'Развернуть меню');
        }
        if (this.titleText) {
            this.titleText.style.display = 'none';
        }
        
        localStorage.setItem(this.storageKey, 'true');
        this.enableTooltips();
    }
    
    expand() {
        this.sidebar.classList.remove('minimized');
        document.body.classList.remove('sidebar-minimized');
        
        if (this.toggleIcon) {
            this.toggleIcon.className = 'bi bi-arrows-angle-contract';
        }
        if (this.toggleButton) {
            this.toggleButton.setAttribute('data-title', 'Свернуть меню');
        }
        if (this.titleText) {
            this.titleText.style.display = 'inline';
        }
        
        localStorage.setItem(this.storageKey, 'false');
        this.disableTooltips();
    }
    
    enableTooltips() {
        const navLinks = document.querySelectorAll('.sidebar .nav-link[data-title]');
        navLinks.forEach(link => {
            link.setAttribute('title', link.getAttribute('data-title'));
        });
    }
    
    disableTooltips() {
        const navLinks = document.querySelectorAll('.sidebar .nav-link[title]');
        navLinks.forEach(link => {
            link.setAttribute('data-title', link.getAttribute('title'));
            link.removeAttribute('title');
        });
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarManager = new SidebarManager();
});

// Глобальная функция для совместимости
window.toggleSidebar = function() {
    if (window.sidebarManager) {
        window.sidebarManager.toggle();
    }
}; 