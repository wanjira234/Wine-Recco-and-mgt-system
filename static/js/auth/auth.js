// Authentication functionality
export function setupAuthentication() {
    setupLoginForm();
    setupRegisterForm();
    setupLogout();
    checkAuthStatus();
}

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        email: formData.get('email'),
                        password: formData.get('password')
                    })
                });
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    showError('Invalid credentials');
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('Login failed');
            }
        });
    }
}

function setupRegisterForm() {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            try {
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        username: formData.get('username'),
                        email: formData.get('email'),
                        password: formData.get('password')
                    })
                });
                if (response.ok) {
                    window.location.href = '/login';
                } else {
                    showError('Registration failed');
                }
            } catch (error) {
                console.error('Registration error:', error);
                showError('Registration failed');
            }
        });
    }
}

function setupLogout() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/auth/logout', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                if (response.ok) {
                    window.location.href = '/login';
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
}

async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/status');
        const data = await response.json();
        updateUI(data.authenticated);
    } catch (error) {
        console.error('Auth status check error:', error);
    }
}

function updateUI(authenticated) {
    const authNav = document.getElementById('auth-nav');
    if (authNav) {
        authNav.innerHTML = authenticated
            ? '<button id="logout-button">Logout</button>'
            : '<a href="/login">Login</a> | <a href="/register">Register</a>';
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
} 