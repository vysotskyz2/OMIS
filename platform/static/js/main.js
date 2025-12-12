const API = {
    baseURL: '/api',

    async request(method, endpoint, data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    getRules() {
        return this.request('GET', '/rules');
    },

    createRule(ruleData) {
        return this.request('POST', '/rules', ruleData);
    },

    getUserContext(userId) {
        return this.request('GET', `/user/context/${userId}`);
    },

    adaptInterface(userId) {
        return this.request('POST', '/user/adapt', { user_id: userId });
    },

    getAnalytics() {
        return this.request('GET', '/analytics');
    }
};

// UI Helper Functions
const UI = {
    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Можно реализовать более сложное отображение уведомлений
    },

    showSuccess(message) {
        this.showNotification(message, 'success');
    },

    showError(message) {
        this.showNotification(message, 'error');
    },

    showLoading(show = true) {
        // Реализация загрузочного спиннера
    },

    updateStats(stats) {
        document.querySelectorAll('[data-stat]').forEach(el => {
            const stat = el.dataset.stat;
            if (stats[stat]) {
                el.textContent = stats[stat];
            }
        });
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('[APP] Приложение загружено');

    // Обработчик форм создания правил
    const ruleForm = document.querySelector('.rule-form');
    if (ruleForm) {
        ruleForm.addEventListener('submit', handleRuleSubmit);
    }

    // Загрузка начальных данных
    loadInitialData();
});

// Handlers
async function handleRuleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const ruleData = {
        name: formData.get('name'),
        description: formData.get('description'),
        priority: parseInt(formData.get('priority')),
        conditions: {
            device_type: formData.get('device_type'),
            time_of_day: formData.get('time_of_day')
        },
        actions: {
            theme: formData.get('theme'),
            layout: formData.get('layout')
        }
    };

    try {
        UI.showLoading(true);
        const result = await API.createRule(ruleData);
        UI.showSuccess(`Правило "${ruleData.name}" создано успешно!`);
        setTimeout(() => window.location.href = '/rules', 1500);
    } catch (error) {
        UI.showError(`Ошибка при создании правила: ${error.message}`);
    } finally {
        UI.showLoading(false);
    }
}

async function loadInitialData() {
    try {
        // Загрузить статистику если на дашборде
        const stats = document.querySelector('[data-page="dashboard"]');
        if (stats) {
            const analytics = await API.getAnalytics();
            console.log('Analytics data:', analytics);
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Utility Functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('ru-RU');
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

console.log('[MAIN.JS] Loaded successfully');