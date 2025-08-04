// Utility Functions

// Local Storage for user management
class UserStorage {
    static setCurrentUser(userData) {
        localStorage.setItem('currentUser', JSON.stringify(userData));
    }

    static getCurrentUser() {
        const userData = localStorage.getItem('currentUser');
        return userData ? JSON.parse(userData) : null;
    }

    static clearCurrentUser() {
        localStorage.removeItem('currentUser');
    }

    static addUser(userData) {
        const users = this.getStoredUsers();
        users[userData.userId] = userData;
        localStorage.setItem('storedUsers', JSON.stringify(users));
    }

    static getStoredUsers() {
        const users = localStorage.getItem('storedUsers');
        return users ? JSON.parse(users) : {};
    }

    static getUserByUsername(username) {
        const users = this.getStoredUsers();
        return Object.values(users).find(user => 
            user.name.toLowerCase() === username.toLowerCase()
        );
    }
}

// UI Utilities
class UIUtils {
    static showResult(elementId, message, isError = false) {
        const resultDiv = document.getElementById(elementId);
        if (!resultDiv) return;

        resultDiv.innerHTML = typeof message === 'object' 
            ? JSON.stringify(message, null, 2) 
            : message;
        
        resultDiv.className = `result ${isError ? 'error' : 'success'}`;
        resultDiv.style.display = 'block';
        
        // Auto-scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    static hideResult(elementId) {
        const resultDiv = document.getElementById(elementId);
        if (resultDiv) {
            resultDiv.style.display = 'none';
        }
    }

    static showLoading(buttonElement, text = 'Loading...') {
        const originalText = buttonElement.textContent;
        buttonElement.innerHTML = `<span class="loading"></span> ${text}`;
        buttonElement.disabled = true;
        
        return () => {
            buttonElement.innerHTML = originalText;
            buttonElement.disabled = false;
        };
    }

    static validateForm(formData, requiredFields) {
        const errors = [];
        
        for (const field of requiredFields) {
            if (!formData[field] || formData[field].toString().trim() === '') {
                errors.push(`${field} is required`);
            }
        }
        
        return errors;
    }

    static formatDate(date) {
        if (!date) return '';
        return new Date(date).toLocaleDateString();
    }

    static formatNumber(num, decimals = 2) {
        return Number(num).toFixed(decimals);
    }
}

// Navigation
class Navigation {
    static showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Show selected page
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        }
        
        // Add active class to corresponding nav item
        const navItem = document.querySelector(`[data-page="${pageId}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
        
        // Hide all results when switching pages
        document.querySelectorAll('.result').forEach(result => {
            result.style.display = 'none';
        });
        
        // Update URL hash
        window.location.hash = pageId;
    }

    static initializeNavigation() {
        // Set up navigation click handlers
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const pageId = item.getAttribute('data-page');
                if (pageId) {
                    Navigation.showPage(pageId);
                }
            });
        });

        // Handle browser back/forward
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash && document.getElementById(hash)) {
                Navigation.showPage(hash);
            }
        });

        // Show initial page from URL hash or default
        const initialPage = window.location.hash.substring(1) || 'register';
        Navigation.showPage(initialPage);
    }
}

// Form Helpers
class FormHelpers {
    static getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};

        const formData = {};
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            const name = input.name || input.id;
            let value = input.value;
            
            // Handle different input types
            if (input.type === 'number') {
                value = value ? parseFloat(value) : null;
            } else if (input.type === 'checkbox') {
                value = input.checked;
            }
            
            if (name && value !== null && value !== '') {
                formData[name] = value;
            }
        });
        
        return formData;
    }

    static clearForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
    }

    static populateForm(formId, data) {
        const form = document.getElementById(formId);
        if (!form) return;

        Object.entries(data).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"], #${key}`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Navigation.initializeNavigation();
    
    // Initialize current user display if available
    const currentUser = UserStorage.getCurrentUser();
    if (currentUser) {
        updateCurrentUserDisplay(currentUser);
    }
});

// Health calculations utility functions
function calculateBMR(weight, height, age, gender) {
    // Using Mifflin-St Jeor Equation
    if (!weight || !height || !age) return 0;
    
    // Convert height to cm if needed
    const heightInCm = height;
    const weightInKg = weight;
    
    // Calculate BMR based on gender
    if (gender && gender.toLowerCase() === 'female') {
        return Math.round((10 * weightInKg) + (6.25 * heightInCm) - (5 * age) - 161);
    } else {
        return Math.round((10 * weightInKg) + (6.25 * heightInCm) - (5 * age) + 5);
    }
}

// Global helper functions
window.UserStorage = UserStorage;
window.UIUtils = UIUtils;
window.Navigation = Navigation;
window.FormHelpers = FormHelpers;
window.calculateBMR = calculateBMR;
