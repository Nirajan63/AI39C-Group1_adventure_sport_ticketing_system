// dashboard.js — Thrill Sphere Personalized Dashboard

const API_URL = 'http://127.0.0.1:5000';

const ACTIVITY_PRICES = {
    paragliding: { name: 'Paragliding',        emoji: '🪂', price: 4500 },
    bungee:      { name: 'Bungee Jumping',      emoji: '🤸', price: 6000 },
    rafting:     { name: 'White-Water Rafting', emoji: '🚣', price: 3200 },
    trekking:    { name: 'Himalayan Trekking',  emoji: '🏔️', price: 8500 },
    zipline:     { name: 'Zip-lining',          emoji: '⚡', price: 3800 },
    canyoning:   { name: 'Canyoning',           emoji: '🌊', price: 4200 },
};

// ── State ──────────────────────────────────────────────────────────
let currentUser   = null;
let allBookings   = [];
let selectedActivity = 'paragliding';

// ── Boot ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Guard: redirect to login if no session
    const stored = localStorage.getItem('ts_user');
    if (!stored) {
        window.location.href = 'login.html';
        return;
    }

    currentUser = JSON.parse(stored);

    setGreeting();
    setLiveDate();
    setInterval(setLiveDate, 60000);

    loadDashboard();
    bindNav();
    bindFilters();
    bindActivityPicker();
    bindBookForm();
    bindLogout();

    // Set min date for booking to today
    const dateInput = document.getElementById('bookDate');
    if (dateInput) {
        dateInput.min = new Date().toISOString().split('T')[0];
    }
});

// ── Greeting ───────────────────────────────────────────────────────
function setGreeting() {
    const hour = new Date().getHours();
    const greet = hour < 12 ? 'Good morning 👋'
                : hour < 17 ? 'Good afternoon 👋'
                : 'Good evening 👋';
    document.getElementById('greeting').textContent = greet;
    document.getElementById('topbarName').textContent = currentUser.username;
    document.getElementById('sidebarName').textContent = currentUser.username;
    document.getElementById('sidebarEmail').textContent = currentUser.email || '';
    document.getElementById('avatarCircle').textContent =
        currentUser.username.charAt(0).toUpperCase();
}

// ── Live date ──────────────────────────────────────────────────────
function setLiveDate() {
    const el = document.getElementById('liveDate');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
}

// ── Load dashboard data from API ───────────────────────────────────
async function loadDashboard() {
    try {
        const res = await fetch(`${API_URL}/dashboard`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser.username })
        });

        const data = await res.json();

        if (!res.ok) {
            console.error('Dashboard error:', data.message);
            return;
        }

        allBookings = data.bookings || [];

        renderStats(data.stats);
        renderRecentBookings(allBookings.slice(-3).reverse());
        renderBookingsFull(allBookings);

    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

// ── Render stat cards ──────────────────────────────────────────────
function renderStats(stats) {
    animateCount('statTotal',    stats.total_bookings);
    animateCount('statUpcoming', stats.upcoming);
    animateCount('statCompleted',stats.completed);

    const spent = stats.total_spent;
    const el = document.getElementById('statSpent');
    if (el) el.textContent = 'NPR ' + spent.toLocaleString();
}

function animateCount(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    let current = 0;
    const step = Math.ceil(target / 30) || 1;
    const timer = setInterval(function () {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current >= target) clearInterval(timer);
    }, 30);
}

// ── Render booking cards ───────────────────────────────────────────
function buildBookingCard(b) {
    const statusClass = b.status === 'confirmed' ? 'confirmed' : 'completed';
    const statusLabel = b.status === 'confirmed' ? '✅ Confirmed' : '🏁 Completed';
    return `
    <div class="booking-card">
        <div class="booking-emoji">${b.emoji}</div>
        <div class="booking-body">
            <div class="booking-name">${b.activity}</div>
            <div class="booking-pills">
                <span>📍 ${b.location}</span>
                <span>📅 ${b.date}</span>
                <span>👥 ${b.people} person${b.people > 1 ? 's' : ''}</span>
                <span>⏱ ${b.duration}</span>
                <span>#${b.id}</span>
            </div>
        </div>
        <div class="booking-right">
            <span class="booking-total">NPR ${b.total.toLocaleString()}</span>
            <span class="booking-status ${statusClass}">${statusLabel}</span>
        </div>
    </div>`;
}

function renderRecentBookings(bookings) {
    const el = document.getElementById('recentList');
    if (!el) return;
    if (!bookings.length) {
        el.innerHTML = '<p class="loading-state">No adventures booked yet.</p>';
        return;
    }
    el.innerHTML = bookings.map(buildBookingCard).join('');
}

function renderBookingsFull(bookings) {
    const el    = document.getElementById('bookingsFull');
    const empty = document.getElementById('emptyBookings');
    if (!el) return;

    if (!bookings.length) {
        el.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    el.innerHTML = bookings.slice().reverse().map(buildBookingCard).join('');
}

// ── Filter tabs ────────────────────────────────────────────────────
function bindFilters() {
    document.querySelectorAll('.filter-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');
            const filtered = filter === 'all'
                ? allBookings
                : allBookings.filter(b => b.status === filter);

            renderBookingsFull(filtered);
        });
    });
}

// ── Sidebar nav ────────────────────────────────────────────────────
function bindNav() {
    document.querySelectorAll('.nav-item[data-section]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            switchSection(link.getAttribute('data-section'));
        });
    });
}

function switchSection(sectionId, activityId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const target = document.getElementById(sectionId);
    if (target) target.classList.add('active');

    const navItem = document.querySelector(`.nav-item[data-section="${sectionId}"]`);
    if (navItem) navItem.classList.add('active');

    if (activityId) {
        selectActivity(activityId);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Activity picker ────────────────────────────────────────────────
function bindActivityPicker() {
    document.querySelectorAll('.activity-option').forEach(function (opt) {
        opt.addEventListener('click', function () {
            selectActivity(opt.getAttribute('data-id'));
        });
    });

    document.getElementById('bookPeople').addEventListener('change', updateTotal);
}

function selectActivity(id) {
    if (!ACTIVITY_PRICES[id]) return;
    selectedActivity = id;

    document.querySelectorAll('.activity-option').forEach(function (opt) {
        opt.classList.toggle('selected', opt.getAttribute('data-id') === id);
    });

    const act = ACTIVITY_PRICES[id];
    const nameEl = document.getElementById('formActivityName');
    if (nameEl) nameEl.textContent = `${act.emoji} ${act.name}`;

    updateTotal();
}

function updateTotal() {
    const people = parseInt(document.getElementById('bookPeople').value) || 1;
    const price  = ACTIVITY_PRICES[selectedActivity].price;
    const el = document.getElementById('bookTotal');
    if (el) el.textContent = 'NPR ' + (price * people).toLocaleString();
}

// ── Book form ──────────────────────────────────────────────────────
function bindBookForm() {
    const btn = document.getElementById('confirmBookBtn');
    if (!btn) return;

    btn.addEventListener('click', async function () {
        const date   = document.getElementById('bookDate').value;
        const people = parseInt(document.getElementById('bookPeople').value);
        const fb     = document.getElementById('bookFeedback');

        if (!date) {
            showFeedback(fb, 'error', 'Please select an adventure date.');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Booking…';

        try {
            const res = await fetch(`${API_URL}/book`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username:    currentUser.username,
                    activity_id: selectedActivity,
                    date:        date,
                    people:      people
                })
            });

            const data = await res.json();

            if (res.ok) {
                showFeedback(fb, 'success', `🎉 Booking confirmed! ID: ${data.booking.id}`);
                allBookings.push(data.booking);
                document.getElementById('bookDate').value = '';
                document.getElementById('bookPeople').value = '1';
                updateTotal();
                // Refresh stats live
                document.getElementById('statTotal').textContent =
                    parseInt(document.getElementById('statTotal').textContent || 0) + 1;
                document.getElementById('statUpcoming').textContent =
                    parseInt(document.getElementById('statUpcoming').textContent || 0) + 1;
                renderRecentBookings(allBookings.slice(-3).reverse());
            } else {
                showFeedback(fb, 'error', data.message || 'Booking failed.');
            }

        } catch (err) {
            showFeedback(fb, 'error', 'Could not connect to server.');
        }

        btn.disabled = false;
        btn.textContent = 'Confirm Booking 🚀';
    });
}

function showFeedback(el, type, msg) {
    el.textContent = msg;
    el.className   = `book-feedback ${type}`;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 4000);
}

// ── Logout ─────────────────────────────────────────────────────────
function bindLogout() {
    document.getElementById('logoutBtn').addEventListener('click', function () {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('ts_user');
            window.location.href = 'login.html';
        }
    });
}
