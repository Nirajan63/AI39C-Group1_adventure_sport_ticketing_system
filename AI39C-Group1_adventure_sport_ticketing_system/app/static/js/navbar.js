(function () {
    const body = document.body;
    const navToggle = document.querySelector(".nav-toggle");
    const navContent = document.querySelector("[data-nav-content]");
    const themeToggle = document.querySelector("[data-theme-toggle]");
    const notificationToggle = document.querySelector("[data-notification-toggle]");
    const notificationMenu = document.querySelector("[data-notification-menu]");
    const navLinks = document.querySelectorAll("[data-nav-link]");
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userMenu = document.getElementById('userMenu');
    const moreOptionsToggle = document.getElementById('moreOptionsToggle');
    const moreOptionsMenu = document.getElementById('moreOptionsMenu');

    const root = document.documentElement;
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        root.classList.add("dark-mode");
    }

    navToggle?.addEventListener("click", function () {
        const isOpen = navContent.classList.toggle("is-open");
        navToggle.setAttribute("aria-expanded", String(isOpen));
        navToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    });
    // User menu toggle
    userMenuToggle?.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = userMenu.classList.toggle('is-open');
        userMenuToggle.setAttribute('aria-expanded', String(isOpen));
    });

    // More Options toggle
    moreOptionsToggle?.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = moreOptionsMenu.classList.toggle('is-open');
        moreOptionsToggle.setAttribute('aria-expanded', String(isOpen));
    });

    themeToggle?.addEventListener("click", function () {
        const isDark = root.classList.toggle("dark-mode");
        localStorage.setItem("theme", isDark ? "dark" : "light");
    });

    notificationToggle?.addEventListener("click", function (event) {
        event.stopPropagation();
        const isOpen = notificationMenu.classList.toggle("is-open");
        notificationToggle.setAttribute("aria-expanded", String(isOpen));
    });

    document.addEventListener("click", function (event) {
        // Close notifications menu if open
        if (notificationMenu && notificationToggle) {
            if (!notificationMenu.contains(event.target) && !notificationToggle.contains(event.target)) {
                notificationMenu.classList.remove("is-open");
                notificationToggle.setAttribute("aria-expanded", "false");
            }
        }
        // Close user menu if open
        if (userMenu && userMenuToggle) {
            if (!userMenu.contains(event.target) && !userMenuToggle.contains(event.target)) {
                userMenu.classList.remove("is-open");
                userMenuToggle.setAttribute("aria-expanded", "false");
            }
        }
        // Close more menu if open
        if (moreOptionsMenu && moreOptionsToggle) {
            if (!moreOptionsMenu.contains(event.target) && !moreOptionsToggle.contains(event.target)) {
                moreOptionsMenu.classList.remove("is-open");
                moreOptionsToggle.setAttribute("aria-expanded", "false");
            }
        }
    });

    const currentPath = window.location.pathname.replace(/\/$/, "") || "/";
    navLinks.forEach(function (link) {
        const linkPath = new URL(link.href).pathname.replace(/\/$/, "") || "/";
        if (linkPath === currentPath) {
            link.classList.add("is-active");
            link.setAttribute("aria-current", "page");
        }
    });
})();