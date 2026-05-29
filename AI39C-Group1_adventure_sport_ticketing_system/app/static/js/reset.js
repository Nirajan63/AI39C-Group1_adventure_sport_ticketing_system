document.addEventListener('DOMContentLoaded', () => {
    const requestForm = document.getElementById('request-otp-form');
    const resetForm = document.getElementById('reset-password-form');
    let userEmail = '';

    // Step 1: Request Password Reset OTP Code
    if (requestForm) {
        requestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('reset-email');
            const sendBtn = document.getElementById('send-otp-btn');
            
            userEmail = emailInput.value.trim();
            if (!userEmail) return;

            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending Verification...';

            try {
                const response = await fetch('/forgot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ action: 'send_otp', email: userEmail })
                });

                const data = await response.json();

                if (response.ok) {
                    // Transition to step 2 panel smoothly
                    requestForm.classList.remove('active');
                    setTimeout(() => {
                        resetForm.classList.add('active');
                    }, 400);
                } else {
                    alert(data.message || 'Failed to send verification code.');
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send Verification Code';
                }
            } catch (err) {
                console.error("Forgot OTP send error:", err);
                alert('Network connection error. Failed to reach the server.');
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send Verification Code';
            }
        });
    }

    // Step 2: Verify OTP and save new password
    if (resetForm) {
        resetForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const otpInput = document.getElementById('reset-otp');
            const newPasswordInput = document.getElementById('new-password');
            const confirmPasswordInput = document.getElementById('confirm-password');
            const resetBtn = document.getElementById('reset-btn');

            const code = otpInput.value.trim();
            const newPassword = newPasswordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            if (newPassword.length < 6) {
                alert('Password must be at least 6 characters long.');
                return;
            }

            resetBtn.disabled = true;
            resetBtn.textContent = 'Updating Password...';

            try {
                const response = await fetch('/forgot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        action: 'reset',
                        email: userEmail,
                        code: code,
                        password: newPassword
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    alert('🎉 Password reset successful! You can now log in.');
                    window.location.href = '/login';
                } else {
                    alert(data.message || 'Failed to reset password.');
                    resetBtn.disabled = false;
                    resetBtn.textContent = 'Update Password';
                }
            } catch (err) {
                console.error("Password reset error:", err);
                alert('Network connection error. Failed to save new password.');
                resetBtn.disabled = false;
                resetBtn.textContent = 'Update Password';
            }
        });
    }
});