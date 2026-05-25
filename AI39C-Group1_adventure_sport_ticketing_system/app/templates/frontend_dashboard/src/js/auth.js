// auth.js — Thrill Sphere Authentication

const API_URL = 'http://127.0.0.1:5000';

// ── Signup ─────────────────────────────────────────────────────────
const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('signup-username').value.trim();
        const email    = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value;

        try {
            const res  = await fetch(`${API_URL}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();

            if (res.ok) {
                alert('Registered successfully!');
                window.location.href = 'login.html';
            } else {
                alert(data.message || 'Registration failed.');
            }
        } catch (err) {
            alert('Failed to connect to the server.');
        }
    });
}

// ── Login ──────────────────────────────────────────────────────────
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        try {
            const res  = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (res.ok) {
                // Save user to localStorage so dashboard can read it
                localStorage.setItem('ts_user', JSON.stringify(data.user));
                window.location.href = 'dashboard.html';
            } else {
                alert(data.message || 'Invalid username or password.');
            }
        } catch (err) {
            alert('Failed to connect to the server.');
        }
    });
}

// ── Forgot Password ────────────────────────────────────────────────
const forgotForm = document.getElementById('forgot-form');
if (forgotForm) {
    forgotForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const newPassword     = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (newPassword !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        try {
            const res  = await fetch(`${API_URL}/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: newPassword })
            });
            const data = await res.json();

            if (res.ok) {
                alert('Password reset successfully!');
                window.location.href = 'login.html';
            } else {
                alert(data.message || 'Failed to reset password.');
            }
        } catch (err) {
            alert('Failed to connect to the server.');
        }
    });
}
