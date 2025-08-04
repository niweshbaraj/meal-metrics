// Main Application Logic

// Global state
let currentUser = null;
let loggedInUser = null; // For tracking the currently logged in user

// Role Management Functions
function switchRole() {
    // Access the currentUser from api.js
    window.currentUser.role = window.currentUser.role === 'user' ? 'admin' : 'user';
    document.getElementById('currentRole').textContent = window.currentUser.role;
    showMessage(`Switched to ${window.currentUser.role} role`, 'success');
    
    // Update UI based on role
    updateUIForRole();
}

function setUserId() {
    const newUserId = document.getElementById('userIdInput').value.trim();
    if (newUserId) {
        window.currentUser.userId = newUserId;
        document.getElementById('currentUserId').textContent = newUserId;
        document.getElementById('userIdInput').value = '';
        showMessage(`User ID set to: ${newUserId}`, 'success');
    }
}

// Login/Logout Functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    populateUserSelectors(); // Populate the login dropdown
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

async function performLogin() {
    const selectedUserId = document.getElementById('loginUserId').value;
    const isAdmin = document.getElementById('adminLogin').checked;
    
    if (!selectedUserId) {
        showMessage('Please select a user to login as', 'error');
        return;
    }
    
    try {
        // Get user details
        const userDetails = await api.getUserDetails(selectedUserId);
        
        // Set the logged in user
        loggedInUser = {
            userId: selectedUserId,
            name: userDetails.name || 'Unknown',
            role: isAdmin ? 'admin' : 'user',
            ...userDetails
        };
        
        // Update global state
        window.currentUser.userId = selectedUserId;
        window.currentUser.role = isAdmin ? 'admin' : 'user';
        
        // Update UI
        document.getElementById('currentUserId').textContent = selectedUserId;
        document.getElementById('currentRole').textContent = loggedInUser.role;
        document.getElementById('loggedInUserName').textContent = loggedInUser.name;
        document.getElementById('loggedInUser').style.display = 'inline';
        document.getElementById('logoutBtn').style.display = 'inline';
        
        // Auto-populate forms with logged in user
        autoPopulateUserForms();
        updateUIForRole();
        
        closeLoginModal();
        showMessage(`Logged in as ${loggedInUser.name} (${loggedInUser.role})`, 'success');
        
        // Show dashboard for regular users
        if (!isAdmin) {
            showPage('dashboard');
            loadUserDashboard();
        }
        
    } catch (error) {
        showMessage(`Login failed: ${error.message}`, 'error');
    }
}

function logout() {
    loggedInUser = null;
    document.getElementById('loggedInUser').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'none';
    document.getElementById('dashboardTab').style.display = 'none';
    document.getElementById('adminTab').style.display = 'none';
    
    // Reset to default user/role
    window.currentUser.userId = 'user1';
    window.currentUser.role = 'user';
    document.getElementById('currentUserId').textContent = 'user1';
    document.getElementById('currentRole').textContent = 'user';
    
    showMessage('Logged out successfully', 'success');
    showPage('register');
}

function updateUIForRole() {
    const isAdmin = window.currentUser.role === 'admin';
    const isLoggedIn = loggedInUser !== null;
    
    // Show/hide tabs based on role and login status
    document.getElementById('dashboardTab').style.display = isLoggedIn && !isAdmin ? 'block' : 'none';
    document.getElementById('adminTab').style.display = isAdmin ? 'block' : 'none';
}

function autoPopulateUserForms() {
    if (!loggedInUser) return;
    
    // Auto-populate user selectors
    const userSelectors = document.querySelectorAll('.user-selector');
    userSelectors.forEach(selector => {
        if (selector.id !== 'loginUserId' && selector.id !== 'adminUserSelect') {
            selector.value = loggedInUser.userId;
        }
    });
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Load current user from storage
    currentUser = UserStorage.getCurrentUser();
    updateCurrentUserDisplay();
    
    // Load available foods on startup
    loadAvailableFoods();
    
    // Set up event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // User selection handlers for forms that need userId
    document.querySelectorAll('.user-selector').forEach(selector => {
        selector.addEventListener('change', handleUserSelection);
    });
}

// Current User Management
function updateCurrentUserDisplay() {
    const userDisplay = document.getElementById('currentUserDisplay');
    const userSelectors = document.querySelectorAll('.user-selector');
    
    if (currentUser && userDisplay) {
        userDisplay.innerHTML = `
            <div class="user-info">
                <h4>Current User: ${currentUser.name}</h4>
                <p><strong>User ID:</strong> ${currentUser.userId}</p>
                <p><strong>Goal:</strong> ${currentUser.goal}</p>
                <button class="btn secondary" onclick="clearCurrentUser()">Switch User</button>
            </div>
        `;
        
        // Pre-select current user in dropdowns
        userSelectors.forEach(selector => {
            selector.value = currentUser.userId;
        });
    } else if (userDisplay) {
        userDisplay.innerHTML = `
            <div class="user-info">
                <p>No user selected. Please register or select a user.</p>
            </div>
        `;
    }
}

function clearCurrentUser() {
    currentUser = null;
    UserStorage.clearCurrentUser();
    updateCurrentUserDisplay();
    populateUserSelectors();
}

// User Registration
async function registerUser() {
    const hideLoading = UIUtils.showLoading(
        document.querySelector('#register .btn'), 
        'Registering...'
    );
    
    try {
        const formData = FormHelpers.getFormData('registerForm');
        
        // Validate required fields
        const requiredFields = ['name', 'age', 'weight', 'height', 'gender'];
        const errors = UIUtils.validateForm(formData, requiredFields);
        
        if (errors.length > 0) {
            UIUtils.showResult('registerResult', `Validation errors: ${errors.join(', ')}`, true);
            return;
        }
        
        const response = await api.registerUser(formData);
        
        if (response.success) {
            // Store user data
            const userData = {
                userId: response.data.userId,
                name: formData.name,
                goal: formData.goal,
                ...formData
            };
            
            UserStorage.addUser(userData);
            UserStorage.setCurrentUser(userData);
            currentUser = userData;
            
            updateCurrentUserDisplay();
            populateUserSelectors();
            
            UIUtils.showResult('registerResult', {
                message: response.data.message,
                userId: response.data.userId,
                bmr: response.data.bmr
            });
            
            // Clear form
            FormHelpers.clearForm('registerForm');
        } else {
            UIUtils.showResult('registerResult', response.data, true);
        }
    } catch (error) {
        UIUtils.showResult('registerResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// User Lookup and Selection
async function populateUserSelectors() {
    const userSelectors = document.querySelectorAll('.user-selector');
    
    try {
        // Get users from API
        const response = await api.listUsers();
        
        if (response.success && response.data.users) {
            const users = response.data.users;
            
            userSelectors.forEach(selector => {
                // Clear existing options except the first one
                while (selector.children.length > 1) {
                    selector.removeChild(selector.lastChild);
                }
                
                // Add user options
                users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.userId;
                    option.textContent = `${user.name} (${user.goal})`;
                    selector.appendChild(option);
                });
                
                // Select current user if available
                if (currentUser) {
                    selector.value = currentUser.userId;
                }
            });
        }
    } catch (error) {
        console.error('Error populating user selectors:', error);
    }
}

function handleUserSelection(event) {
    const userId = event.target.value;
    if (userId) {
        // Find user data
        const users = UserStorage.getStoredUsers();
        const selectedUser = users[userId];
        
        if (selectedUser) {
            currentUser = selectedUser;
            UserStorage.setCurrentUser(selectedUser);
            updateCurrentUserDisplay();
        }
    }
}

// BMR Functions
async function getBMR() {
    const userId = document.getElementById('bmrUserId').value;
    
    if (!userId) {
        UIUtils.showResult('bmrResult', 'Please select a user', true);
        return;
    }
    
    const hideLoading = UIUtils.showLoading(
        document.querySelector('#bmr .btn'), 
        'Calculating...'
    );
    
    try {
        const response = await api.getUserBMR(userId);
        
        if (response.success) {
            UIUtils.showResult('bmrResult', {
                bmr: `${response.data.bmr} calories/day`,
                formula: response.data.formula,
                user_profile: response.data.user_profile
            });
        } else {
            UIUtils.showResult('bmrResult', response.data, true);
        }
    } catch (error) {
        UIUtils.showResult('bmrResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Meal Logging
async function logMeal() {
    const userId = document.getElementById('mealUserId').value;
    const meal = document.getElementById('mealType').value;
    const itemsText = document.getElementById('mealItems').value;

    if (!userId || !meal || !itemsText) {
        UIUtils.showResult('mealResult', 'Please fill in all fields', true);
        return;
    }

    const hideLoading = UIUtils.showLoading(
        document.querySelector('#meal .btn'), 
        'Logging meal...'
    );

    try {
        const items = itemsText.split(',').map(item => item.trim()).filter(item => item);

        const mealData = {
            userId: userId,
            meal: meal,
            items: items
        };

        const response = await api.logMeal(mealData);

        if (response.success) {
            UIUtils.showResult('mealResult', 'Meal has been successfully logged!', false);

            // Clear meal items
            document.getElementById('mealItems').value = '';
        } else {
            UIUtils.showResult('mealResult', 'Failed to log the meal. Please try again.', true);
        }
    } catch (error) {
        console.error('Error in logMeal:', error);
        UIUtils.showResult('mealResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

async function getUserMeals() {
    const userId = document.getElementById('statusUserId').value;
    const date = document.getElementById('statusDate').value;

    if (!userId) {
        UIUtils.showResult('statusResult', 'Please select a user', true);
        return;
    }

    const hideLoading = UIUtils.showLoading(
        document.querySelector('#status .btn[onclick="getUserMeals()"]'), 
        'Loading meals...'
    );

    try {
        const response = await api.getUserMeals(userId, date);
        console.log('getUserMeals Response:', response); // Debug log

        if (response.success) {
            UIUtils.showResult('statusResult', {
                username: response.data.username,
                date_filter: response.data.date_filter,
                total_meals: response.data.total_meals,
                meals: response.data.meals,
                total_nutrition: response.data.total_nutrition
            }, false);
        } else {
            UIUtils.showResult('statusResult', response.data, true);
        }
    } catch (error) {
        console.error('Error in getUserMeals:', error);
        UIUtils.showResult('statusResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

async function getNutritionStatus() {
    const userId = document.getElementById('statusUserId').value;
    const date = document.getElementById('statusDate').value;

    if (!userId) {
        UIUtils.showResult('statusResult', 'Please select a user', true);
        return;
    }

    const hideLoading = UIUtils.showLoading(
        document.querySelector('#status .btn[onclick="getNutritionStatus()"]'), 
        'Loading status...'
    );

    try {
        const response = await api.getNutritionStatus(userId, date);
        console.log('getNutritionStatus Response:', response); // Debug log

        if (response.success) {
            UIUtils.showResult('statusResult', {
                username: response.data.username,
                date: response.data.date,
                bmr: `${response.data.bmr} calories/day`,
                nutrient_intake: response.data.nutrient_intake,
                meals_logged: response.data.meals_logged,
                recommendations: response.data.recommendations
            }, false);
        } else {
            UIUtils.showResult('statusResult', response.data, true);
        }
    } catch (error) {
        console.error('Error in getNutritionStatus:', error);
        UIUtils.showResult('statusResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Food Management
let availableFoods = [];

async function loadAvailableFoods() {
    try {
        const response = await api.getFoods();
        if (response.success) {
            availableFoods = Object.keys(response.data.foods);
            updateFoodSuggestions();
        }
    } catch (error) {
        console.error('Error loading foods:', error);
    }
}

function updateFoodSuggestions() {
    const mealItemsInput = document.getElementById('mealItems');
    if (mealItemsInput) {
        mealItemsInput.setAttribute('placeholder', 
            `Available foods: ${availableFoods.slice(0, 5).join(', ')}...`
        );
    }
}

async function showAvailableFoods() {
    const hideLoading = UIUtils.showLoading(
        document.querySelector('#meal .btn.secondary'), 
        'Loading foods...'
    );
    
    try {
        const response = await api.getFoods();
        
        if (response.success) {
            UIUtils.showResult('mealResult', {
                total_foods: response.data.total_foods,
                categories: response.data.categories,
                foods: response.data.foods
            });
        } else {
            UIUtils.showResult('mealResult', response.data, true);
        }
    } catch (error) {
        UIUtils.showResult('mealResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Webhook Testing
async function testWebhook() {
    const userId = document.getElementById('webhookUserId').value;
    const message = document.getElementById('webhookMessage').value;
    
    if (!userId || !message) {
        UIUtils.showResult('webhookResult', 'Please select a user and enter a message', true);
        return;
    }
    
    const hideLoading = UIUtils.showLoading(
        document.querySelector('#webhook .btn'), 
        'Sending webhook...'
    );
    
    try {
        const webhookData = {
            userId: userId,
            message: message
        };
        
        const response = await api.sendWebhook(webhookData);
        
        if (response.success) {
            UIUtils.showResult('webhookResult', {
                status: response.data.status,
                message: response.data.message,
                webhook_data: response.data.webhook_data,
                result: response.data.result
            });
        } else {
            UIUtils.showResult('webhookResult', response.data, true);
        }
    } catch (error) {
        UIUtils.showResult('webhookResult', `Error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Send Webhook Message
async function sendWebhook() {
    const message = document.getElementById('webhookMessageInput').value.trim();
    if (!message) {
        showMessage('Please enter a message to send', 'error');
        return;
    }

    try {
        const response = await api.sendWebhookMessage(message);
        if (response.success) {
            showMessage('Webhook message sent successfully', 'success');
            loadUserDashboard(); // Refresh the dashboard after sending the message
        } else {
            showMessage(`Webhook response error: ${response.data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`Error sending webhook: ${error.message}`, 'error');
    }
}

// Load users when the app starts
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(populateUserSelectors, 500); // Small delay to ensure API is ready
});

// Dashboard Functions
async function loadUserDashboard() {
    try {
        const userId = window.currentUser.userId;
        const today = new Date().toISOString().split('T')[0];

        // Fetch meals and nutrition status
        const mealsResponse = await api.request(`/meals/${userId}?on_date=${today}`);
        const nutritionResponse = await api.request(`/nutrition/status/${userId}?on_date=${today}`);

        if (mealsResponse.success && nutritionResponse.success) {
            // Update meal history
            const mealHistory = document.getElementById('mealHistory');
            mealHistory.innerHTML = '';
            mealsResponse.data.meals.forEach(meal => {
                const mealItem = document.createElement('li');
                mealItem.textContent = `${meal.meal} - ${meal.items.join(', ')} (Logged at: ${meal.loggedAt})`;
                mealHistory.appendChild(mealItem);
            });

            // Update nutrient intake overview
            const nutrientIntake = nutritionResponse.data.nutrient_intake;
            document.getElementById('caloriesIntake').textContent = nutrientIntake.calories;
            document.getElementById('proteinIntake').textContent = nutrientIntake.protein;
            document.getElementById('carbsIntake').textContent = nutrientIntake.carbs;
            document.getElementById('fiberIntake').textContent = nutrientIntake.fiber;
        } else {
            showMessage('Error loading dashboard data', 'error');
        }
    } catch (error) {
        showMessage(`Error loading dashboard: ${error.message}`, 'error');
    }
}

// Admin Functions
async function adminViewUserBMR() {
    const selectedUserId = document.getElementById('adminUserSelect').value;
    if (!selectedUserId) {
        showAdminResult('Please select a user first', true);
        return;
    }
    
    try {
        const response = await api.getUserBMR(selectedUserId);
        showAdminResult(response, false);
    } catch (error) {
        showAdminResult(`Error: ${error.message}`, true);
    }
}

async function adminViewUserMeals() {
    const selectedUserId = document.getElementById('adminUserSelect').value;
    if (!selectedUserId) {
        showAdminResult('Please select a user first', true);
        return;
    }
    
    try {
        const response = await api.getUserMeals(selectedUserId);
        showAdminResult(response, false);
    } catch (error) {
        showAdminResult(`Error: ${error.message}`, true);
    }
}

async function adminViewUserNutrition() {
    const selectedUserId = document.getElementById('adminUserSelect').value;
    if (!selectedUserId) {
        showAdminResult('Please select a user first', true);
        return;
    }
    
    try {
        const response = await api.getNutritionStatus(selectedUserId);
        showAdminResult(response, false);
    } catch (error) {
        showAdminResult(`Error: ${error.message}`, true);
    }
}

async function adminViewAllUsers() {
    try {
        const response = await api.listUsers();
        showAdminResult(response, false);
    } catch (error) {
        showAdminResult(`Error: ${error.message}`, true);
    }
}

function showAdminResult(data, isError) {
    const resultDiv = document.getElementById('adminResults');
    resultDiv.style.display = 'block';
    resultDiv.className = `result ${isError ? 'error' : 'success'}`;
    
    if (typeof data === 'object') {
        resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } else {
        resultDiv.textContent = data;
    }
}

// Page Navigation
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    
    // Add active class to corresponding nav item
    const navItem = document.querySelector(`[data-page="${pageId}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    // Auto-populate forms if user is logged in
    if (loggedInUser && pageId !== 'admin') {
        setTimeout(autoPopulateUserForms, 100);
    }
    
    // Load dashboard data if dashboard page
    if (pageId === 'dashboard') {
        loadUserDashboard();
    }
}

// Add click handlers for navigation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const pageId = item.getAttribute('data-page');
            showPage(pageId);
        });
    });
});
