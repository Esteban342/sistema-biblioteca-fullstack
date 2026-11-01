import { api } from './api.js';

export function inicializarAuth() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('btnLogin');
            const errorDiv = document.getElementById('loginError');
            btn.textContent = 'Verificando...'; btn.disabled = true; errorDiv.textContent = '';
            
            try {
                const data = await api.login(
                    document.getElementById('username').value, 
                    document.getElementById('password').value
                );
                if (data.success) {
                    sessionStorage.setItem('user', JSON.stringify(data));
                    window.location.href = '/dashboard';
                } else {
                    errorDiv.textContent = data.error || 'Credenciales incorrectas';
                    btn.textContent = 'Ingresar'; btn.disabled = false;
                }
            } catch (error) {
                errorDiv.textContent = 'Error de conexión';
                btn.textContent = 'Ingresar'; btn.disabled = false;
            }
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sessionStorage.removeItem('user');
            window.location.href = '/';
        });
    }
}