// Main JavaScript file for Ajeer Dashboard

// Utility function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, options);
        return await response.json();
    } catch (error) {
        console.error('[v0] API Call Error:', error);
        throw error;
    }
}

// Utility function to format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.minWidth = '300px';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, duration);
}

// Page loading indicator
function showLoadingIndicator() {
    const loader = document.createElement('div');
    loader.id = 'loadingIndicator';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    loader.innerHTML = '<div style="color: white; font-size: 1.5rem;">Loading...</div>';
    document.body.appendChild(loader);
}

function hideLoadingIndicator() {
    const loader = document.getElementById('loadingIndicator');
    if (loader) {
        loader.remove();
    }
}

// Initialize tooltips (if you want to add tooltips)
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', () => {
            const tooltip = document.createElement('div');
            tooltip.textContent = element.getAttribute('data-tooltip');
            tooltip.style.cssText = `
                position: absolute;
                background-color: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                font-size: 0.85rem;
                white-space: nowrap;
                pointer-events: none;
            `;
            element.appendChild(tooltip);
        });

        element.addEventListener('mouseleave', () => {
            const tooltip = element.querySelector('div');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

// Document ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[v0] Ajeer Dashboard initialized');
    initializeTooltips();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('[v0] Global Error:', event.error);
    showNotification('An error occurred. Please try again.', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('[v0] Unhandled Promise Rejection:', event.reason);
    showNotification('An error occurred. Please try again.', 'error');
});
