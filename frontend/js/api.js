// Configuration
const CONFIG = {
    API_BASE: window.location.origin + '/api/v1', // Use current domain for API calls
    USER_API_KEY: 'SECRET_API_KEY',
    ADMIN_API_KEY: 'ADMIN_API_KEY'
};

// Current user state (accessible globally)
window.currentUser = {
    role: 'user',
    userId: 'user1'
};

// API Headers
const getHeaders = (includeAuth = true) => {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (includeAuth) {
        const apiKey = window.currentUser.role === 'admin' ? CONFIG.ADMIN_API_KEY : CONFIG.USER_API_KEY;
        headers['X-API-Key'] = apiKey;
        
        if (window.currentUser && window.currentUser.userId) {
            headers['user-id'] = window.currentUser.userId; // Use lowercase 'user-id'
        }

        console.log('Headers:', headers); // Debug log
    }

    return headers;
};

// API Client
class APIClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...getHeaders(options.requireAuth !== false),
                ...options.headers
            }
        };

        console.log('Request Config:', config); // Debug log

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            return {
                success: response.ok,
                data: data,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                status: 0
            };
        }
    }

    // User endpoints
    async registerUser(userData) {
        return this.request('/users/register', {
            method: 'POST',
            body: JSON.stringify(userData),
            requireAuth: false // Registration doesn't require auth
        });
    }

    async getUserByUsername(username) {
        return this.request(`/users/lookup/${encodeURIComponent(username)}`);
    }

    async getUserBMR(userId) {
        return this.request(`/users/bmr/${userId}`);
    }

    async getUserDetails(userId) {
        // For non-admin users, we'll need to get user details from BMR endpoint
        // since list users requires admin access
        try {
            if (window.currentUser.role === 'admin') {
                const users = await this.listUsers();
                const user = users.users.find(u => u.userId === userId);
                if (!user) {
                    throw new Error('User not found');
                }
                return user;
            } else {
                // For regular users, get basic info from BMR endpoint
                const bmrData = await this.getUserBMR(userId);
                return {
                    userId: userId,
                    name: bmrData.username || 'Unknown',
                    ...bmrData.user_profile
                };
            }
        } catch (error) {
            throw new Error(`Failed to get user details: ${error.message}`);
        }
    }

    async listUsers() {
        return this.request('/users/');
    }

    // Meal endpoints
    async logMeal(mealData) {
        return this.request('/meals/log', {
            method: 'POST',
            body: JSON.stringify(mealData)
        });
    }

    async getUserMeals(userId, date = null) {
        let endpoint = `/meals/${userId}`;
        if (date) {
            endpoint += `?on_date=${date}`;
        }
        return this.request(endpoint);
    }

    // Nutrition endpoints
    async getNutritionStatus(userId, date = null) {
        let endpoint = `/nutrition/status/${userId}`;
        if (date) {
            endpoint += `?on_date=${date}`;
        }
        return this.request(endpoint);
    }

    // User management functions
    async getPublicUsers() {
        return this.request('/users/public', {
            requireAuth: false // Public endpoint doesn't require auth
        });
    }

    async getAllUsers() {
        return this.request('/users/');
    }

    async getUser(userId) {
        return this.request(`/users/${userId}`);
    }

    async getFoods() {
        return this.request('/nutrition/foods', {
            requireAuth: false // Foods list doesn't require auth
        });
    }

    // Webhook endpoint
    async sendWebhook(webhookData) {
        const { userId, ...payload } = webhookData; // Exclude userId from the payload
        try {
            return await this.request('/webhook/', {
                method: 'POST',
                body: JSON.stringify(payload),
                headers: getHeaders() // Include headers with X-User-Id
            });
        } catch (error) {
            console.error('Error sending webhook:', error);
            throw error;
        }
    }

    async sendWebhookMessage(message) {
        console.log('Sending webhook message with user ID:', window.currentUser.userId); // Debug log
        try {
            return await this.request('/webhook', {
                method: 'POST',
                body: JSON.stringify({ message }),
                headers: getHeaders() // Use getHeaders to include headers
            });
        } catch (error) {
            console.error('Error sending webhook message:', error);
            throw error;
        }
    }
}

// Create global API instance
window.api = new APIClient();
