const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Login successful!');
                    localStorage.setItem('user', JSON.stringify(data.user || { username: username }));
                    window.location.href = '/dashboard';
                } else {
                    alert(data.message || 'Invalid username or password.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to connect to the server.');
            }
        });
    }

    const googleLoginBtn = document.getElementById('google-login-btn');
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', openGoogleSignIn);
    }
});

function openGoogleSignIn() {
    if (GOOGLE_CLIENT_ID === 'YOUR_GOOGLE_CLIENT_ID' || GOOGLE_CLIENT_ID === '') {
        const width = 500;
        const height = 600;
        const left = (window.screen.width / 2) - (width / 2);
        const top = (window.screen.height / 2) - (height / 2);
        window.open('/static/mock_google_login.html', 'Google Sign In', `width=${width},height=${height},left=${left},top=${top}`);
    } else {
        const redirectUri = window.location.origin + '/login';
        const oauthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=email%20profile`;
        window.location.href = oauthUrl;
    }
}

window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'mock-google-login') {
        const email = event.data.email;
        const username = event.data.username || email.split('@')[0];
        alert(`Logged in via Google as: ${email}`);
        localStorage.setItem('user', JSON.stringify({ username: username, email: email }));
        window.location.href = '/dashboard';
    }
});

// Check if returning from real Google OAuth redirect hash
const hash = window.location.hash;
if (hash) {
    const params = new URLSearchParams(hash.substring(1));
    const accessToken = params.get('access_token');
    if (accessToken) {
        fetch(`https://www.googleapis.com/oauth2/v3/userinfo?access_token=${accessToken}`)
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Google verification failed.');
            })
            .then(userInfo => {
                alert(`Logged in via Google as: ${userInfo.email}`);
                localStorage.setItem('user', JSON.stringify({ username: userInfo.name || userInfo.email, email: userInfo.email }));
                window.location.href = '/dashboard';
            })
            .catch(error => {
                console.error('Google Auth Verification Error:', error);
                alert('Error verifying Google credentials.');
            });
    }
}
