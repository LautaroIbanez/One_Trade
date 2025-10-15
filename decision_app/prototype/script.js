// One Trade Decision App - Prototype JavaScript

// Navigation functionality
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links and pages
            navLinks.forEach(l => l.classList.remove('active'));
            pages.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Show corresponding page
            const pageId = link.getAttribute('data-page');
            const page = document.getElementById(pageId);
            if (page) {
                page.classList.add('active');
            }
        });
    });
}

// Show specific page (for buttons)
function showPage(pageId) {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    
    // Remove active class from all links and pages
    navLinks.forEach(l => l.classList.remove('active'));
    pages.forEach(p => p.classList.remove('active'));
    
    // Add active class to corresponding link
    const link = document.querySelector(`[data-page="${pageId}"]`);
    if (link) {
        link.classList.add('active');
    }
    
    // Show page
    const page = document.getElementById(pageId);
    if (page) {
        page.classList.add('active');
    }
}

// Simulate real-time data updates
function simulateDataUpdates() {
    // Update price with random changes
    const priceElement = document.querySelector('.price');
    if (priceElement) {
        const currentPrice = parseFloat(priceElement.textContent.replace('$', '').replace(',', ''));
        const change = (Math.random() - 0.5) * 100; // Random change between -50 and +50
        const newPrice = currentPrice + change;
        priceElement.textContent = `$${newPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    
    // Update price change indicator
    const priceChangeElement = document.querySelector('.price-change');
    if (priceChangeElement) {
        const change = (Math.random() - 0.5) * 4; // Random change between -2% and +2%
        const sign = change >= 0 ? '+' : '';
        priceChangeElement.textContent = `${sign}${change.toFixed(1)}% (24h)`;
        priceChangeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
    }
    
    // Update confidence meter
    const confidenceElement = document.querySelector('.summary-value');
    if (confidenceElement && confidenceElement.textContent.includes('%')) {
        const currentConfidence = parseInt(confidenceElement.textContent);
        const change = Math.floor((Math.random() - 0.5) * 10); // Random change between -5 and +5
        const newConfidence = Math.max(50, Math.min(95, currentConfidence + change));
        confidenceElement.textContent = `${newConfidence}%`;
    }
}

// Add interactive elements
function addInteractivity() {
    // Add click handlers for metric cards
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.addEventListener('click', () => {
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 150);
        });
    });
    
    // Add hover effects for table rows
    const tableRows = document.querySelectorAll('.data-table tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = 'var(--neutral-50)';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });
    });
    
    // Add form validation
    const formInputs = document.querySelectorAll('.form-input');
    formInputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (input.value.trim() === '') {
                input.style.borderColor = 'var(--error)';
            } else {
                input.style.borderColor = 'var(--success)';
            }
        });
    });
}

// Simulate loading states
function simulateLoading() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (button.textContent.includes('Guardar') || button.textContent.includes('Nuevo')) {
                e.preventDefault();
                
                // Add loading state
                const originalText = button.textContent;
                button.textContent = '⏳ Cargando...';
                button.disabled = true;
                button.classList.add('loading');
                
                // Simulate API call
                setTimeout(() => {
                    button.textContent = '✅ Completado';
                    button.style.backgroundColor = 'var(--success)';
                    
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                        button.classList.remove('loading');
                        button.style.backgroundColor = '';
                    }, 2000);
                }, 1500);
            }
        });
    });
}

// Add keyboard shortcuts
function addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Alt + 1-4 for navigation
        if (e.altKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    showPage('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    showPage('history');
                    break;
                case '3':
                    e.preventDefault();
                    showPage('backtests');
                    break;
                case '4':
                    e.preventDefault();
                    showPage('settings');
                    break;
            }
        }
        
        // Escape to go back to dashboard
        if (e.key === 'Escape') {
            showPage('dashboard');
        }
    });
}

// Add tooltips
function addTooltips() {
    const elementsWithTitle = document.querySelectorAll('[title]');
    elementsWithTitle.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.getAttribute('title');
            tooltip.style.cssText = `
                position: absolute;
                background: var(--neutral-800);
                color: white;
                padding: var(--space-2) var(--space-3);
                border-radius: var(--radius-md);
                font-size: var(--text-xs);
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            
            setTimeout(() => {
                tooltip.style.opacity = '1';
            }, 10);
            
            element.addEventListener('mouseleave', () => {
                tooltip.remove();
            });
        });
    });
}

// Add dark mode toggle
function addDarkModeToggle() {
    const darkModeToggle = document.createElement('button');
    darkModeToggle.innerHTML = '🌙';
    darkModeToggle.className = 'btn-icon';
    darkModeToggle.title = 'Toggle Dark Mode';
    darkModeToggle.style.marginLeft = 'var(--space-2)';
    
    const navActions = document.querySelector('.nav-actions');
    navActions.appendChild(darkModeToggle);
    
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        darkModeToggle.innerHTML = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
        
        // Save preference
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
    
    // Load saved preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '☀️';
    }
}

// Add notification system
function addNotificationSystem() {
    const notificationContainer = document.createElement('div');
    notificationContainer.id = 'notifications';
    notificationContainer.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    `;
    document.body.appendChild(notificationContainer);
    
    // Function to show notification
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            background: white;
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-md);
            padding: var(--space-3) var(--space-4);
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;
        
        if (type === 'success') {
            notification.style.borderLeftColor = 'var(--success)';
            notification.style.borderLeftWidth = '4px';
        } else if (type === 'error') {
            notification.style.borderLeftColor = 'var(--error)';
            notification.style.borderLeftWidth = '4px';
        }
        
        notificationContainer.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    };
}

// Simulate notifications
function simulateNotifications() {
    const notifications = [
        { message: 'Nueva recomendación disponible', type: 'info' },
        { message: 'Backtest completado exitosamente', type: 'success' },
        { message: 'Error en conexión con API', type: 'error' },
        { message: 'Configuración guardada', type: 'success' }
    ];
    
    // Show random notification every 30 seconds
    setInterval(() => {
        const notification = notifications[Math.floor(Math.random() * notifications.length)];
        showNotification(notification.message, notification.type);
    }, 30000);
}

// Add search functionality
function addSearchFunctionality() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Buscar...';
    searchInput.className = 'form-input';
    searchInput.style.cssText = `
        width: 200px;
        margin-left: var(--space-4);
    `;
    
    const navActions = document.querySelector('.nav-actions');
    navActions.insertBefore(searchInput, navActions.firstChild);
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const tableRows = document.querySelectorAll('.data-table tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Initialize all functionality
function init() {
    initNavigation();
    addInteractivity();
    simulateLoading();
    addKeyboardShortcuts();
    addTooltips();
    addDarkModeToggle();
    addNotificationSystem();
    addSearchFunctionality();
    
    // Start data simulation
    setInterval(simulateDataUpdates, 5000);
    
    // Start notification simulation
    setTimeout(simulateNotifications, 10000);
    
    // Show welcome notification
    setTimeout(() => {
        showNotification('¡Bienvenido a One Trade Decision App!', 'success');
    }, 1000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Add CSS for dark mode
const darkModeCSS = `
.dark-mode {
    --neutral-50: #0F172A;
    --neutral-100: #1E293B;
    --neutral-200: #334155;
    --neutral-300: #475569;
    --neutral-400: #64748B;
    --neutral-500: #94A3B8;
    --neutral-600: #CBD5E1;
    --neutral-700: #E2E8F0;
    --neutral-800: #F1F5F9;
    --neutral-900: #F8FAFC;
}

.dark-mode body {
    background-color: var(--neutral-50);
    color: var(--neutral-800);
}

.dark-mode .navbar,
.dark-mode .sidebar,
.dark-mode .decision-card,
.dark-mode .chart-section,
.dark-mode .metrics-section,
.dark-mode .history-stats,
.dark-mode .backtest-comparison,
.dark-mode .recent-backtests,
.dark-mode .settings-section {
    background: var(--neutral-100);
    border-color: var(--neutral-200);
}

.dark-mode .nav-link:hover {
    background: var(--neutral-200);
}

.dark-mode .data-table th {
    background: var(--neutral-200);
}

.dark-mode .signals-table th {
    background: var(--neutral-200);
}
`;

// Inject dark mode CSS
const style = document.createElement('style');
style.textContent = darkModeCSS;
document.head.appendChild(style);


