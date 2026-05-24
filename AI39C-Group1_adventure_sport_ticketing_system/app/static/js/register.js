const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID';

document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('signup-username').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;

            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Registered successfully!');
                    window.location.href = '/login';
                } else {
                    alert(data.message || 'Registration failed.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to connect to the server.');
            }
        });
    }

    const googleSignupBtn = document.getElementById('google-signup-btn');
    if (googleSignupBtn) {
        googleSignupBtn.addEventListener('click', openGoogleSignIn);
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
