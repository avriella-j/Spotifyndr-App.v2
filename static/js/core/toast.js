// static/js/core/toast.js — Toast notification system
class Toast {
    // Show a toast notification (3s auto-remove)
    static show(title, message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <h4>${title}</h4>
            <p>${message}</p>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    // Shorthand for success toast
    static success(title, message) {
        this.show(title, message, 'success');
    }
    
    // Shorthand for error toast
    static error(title, message) {
        this.show(title, message, 'error');
    }
}
