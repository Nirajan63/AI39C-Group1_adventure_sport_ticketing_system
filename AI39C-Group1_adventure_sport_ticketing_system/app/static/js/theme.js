document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;
    
    
    const isDark = document.documentElement.classList.contains('dark-mode');
    if (themeIcon) {
        if (isDark) {
            themeIcon.className = 'bx bx-sun';
        } else {
            themeIcon.className = 'bx bx-moon';
        }
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const wasDark = document.documentElement.classList.contains('dark-mode');
            if (wasDark) {
                document.documentElement.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
                if (themeIcon) themeIcon.className = 'bx bx-moon';
            } else {
                document.documentElement.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) themeIcon.className = 'bx bx-sun';
            }
        });
    }
});
