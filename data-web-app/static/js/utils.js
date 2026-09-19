/**
 * Road - Utility Functions
 */

const Utils = {
    // Storage helpers
    getFromStorage: (key) => {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    setToStorage: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    },
    removeFromStorage: (key) => {
        localStorage.removeItem(key);
    },
    
    // Format date
    formatDate: (date, formatType = 'short') => {
        if (!date) return '';
        const d = new Date(date);
        if (isNaN(d.getTime())) return date;
        const format = CONFIG.dateFormat[formatType] || CONFIG.dateFormat.short;
        return d.toLocaleDateString('fr-FR', format);
    },
    
    // Format date for input
    formatDateForInput: (date) => {
        if (!date) return '';
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    
    // Parse date from input
    parseDateFromInput: (dateString) => {
        if (!dateString) return null;
        return new Date(dateString).toISOString();
    },
    
    // Get category color
    getCategoryColor: (category) => {
        return CONFIG.defaultCategoryColors[category] || '#666666';
    },
    
    // Capitalize first letter
    capitalize: (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    // Truncate text
    truncate: (text, length = 50) => {
        if (!text) return '';
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    },
    
    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Generate unique ID
    generateId: () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};
