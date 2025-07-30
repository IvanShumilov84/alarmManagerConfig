/**
 * Утилиты для приложения
 */
class AppUtils {
    /**
     * Управление анимированными рамками сообщений
     */
    static handleBlinkingMessages() {
        const errorMessages = document.querySelectorAll('.alert-danger');
        errorMessages.forEach(message => {
            message.style.animation = 'blinkBorder 1s ease-in-out infinite';
            message.style.border = '3px solid #dc3545';
            message.style.boxShadow = '0 0 15px rgba(220, 53, 69, 0.7)';
            message.style.position = 'relative';
            message.style.zIndex = '10';
            
            setTimeout(() => {
                message.style.animation = 'none';
                message.style.border = '1px solid #dc3545';
                message.style.boxShadow = 'none';
            }, 3000);
        });
    }
    
    /**
     * Инициализация приложения
     */
    static init() {
        this.handleBlinkingMessages();
        
        // Дополнительная проверка через 1 секунду
        setTimeout(() => {
            this.handleBlinkingMessages();
        }, 1000);
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    AppUtils.init();
}); 