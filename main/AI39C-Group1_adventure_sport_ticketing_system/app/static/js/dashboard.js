// dashboard.js — Thrill Sphere Dashboard

document.addEventListener('DOMContentLoaded', function () {
    setGreeting();
    setLiveDate();
    animateCounters();
    bindFilterTabs();
    bindActivityPicker();
    bindBookForm();
});

// ── Greeting ───────────────────────────────────────────────────────
function setGreeting() {
    var h = new Date().getHours();
    var key = h < 12 ? 'dash.good-morning' : h < 17 ? 'dash.good-afternoon' : 'dash.good-evening';
    var el = document.getElementById('greeting');
    if (el) {
        el.setAttribute('data-i18n', key);
        if (window.ThrillLang && window.ThrillLang.getLang) {
            var lang = window.ThrillLang.getLang();
            // Use translate if available
            var trans = window.ThrillLang.translate ? window.ThrillLang.translate(key, lang) : null;
            if (trans) {
                el.textContent = trans;
                return;
            }
        }
        var g = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
        el.textContent = g;
    }
}

// ── Live date ──────────────────────────────────────────────────────
function setLiveDate() {
    var el = document.getElementById('liveDate');
    if (!el) return;
    var lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
    el.textContent = new Date().toLocaleDateString(lang === 'ne' ? 'ne-NP' : 'en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
}

// ── Animate stat counters ──────────────────────────────────────────
function animateCounters() {
    document.querySelectorAll('.stat-value[data-target]').forEach(function (el) {
        var target = parseInt(el.getAttribute('data-target'), 10);
        if (isNaN(target)) return;
        var current = 0;
        var step = Math.ceil(target / 30) || 1;
        var timer = setInterval(function () {
            current = Math.min(current + step, target);
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 30);
    });
}

// ── Section switching ──────────────────────────────────────────────
function switchSection(id, navEl) {
    document.querySelectorAll('.dash-section').forEach(function (s) { s.classList.remove('active'); });
    document.querySelectorAll('.nav-item').forEach(function (n) { n.classList.remove('active'); });

    var target = document.getElementById(id);
    if (target) target.classList.add('active');

    if (navEl) {
        navEl.classList.add('active');
    } else {
        // find matching nav item by onclick
        document.querySelectorAll('.nav-item').forEach(function (n) {
            if (n.getAttribute('onclick') && n.getAttribute('onclick').indexOf("'" + id + "'") !== -1) {
                n.classList.add('active');
            }
        });
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Filter tabs (Bookings section) ────────────────────────────────
function bindFilterTabs() {
    var btns = document.querySelectorAll('.filter-btn');
    btns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            btns.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');

            var filter = btn.getAttribute('data-filter');
            var cards  = document.querySelectorAll('#bookingsFull .booking-card');
            cards.forEach(function (card) {
                var status = card.getAttribute('data-status');
                if (filter === 'all' || status === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// ── Activity picker ────────────────────────────────────────────────
function selectActivity(id) {
    var opts = document.querySelectorAll('.activity-option');
    opts.forEach(function (opt) {
        opt.classList.toggle('selected', opt.getAttribute('data-id') === id);
    });

    var selected = document.querySelector('.activity-option[data-id="' + id + '"]');
    if (!selected) return;

    var price = parseInt(selected.getAttribute('data-price'), 10);
    var name  = selected.getAttribute('data-name');

    document.getElementById('activityIdInput').value = id;
    document.getElementById('formActivityTitle').textContent = name;
    updateTotal(price);
}

function bindActivityPicker() {
    // Set min date
    var dateInput = document.getElementById('bookDate');
    if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

    // People change recalculates total
    var peopleSelect = document.getElementById('bookPeople');
    if (peopleSelect) {
        peopleSelect.addEventListener('change', function () {
            var selected = document.querySelector('.activity-option.selected');
            if (selected) updateTotal(parseInt(selected.getAttribute('data-price'), 10));
        });
    }
}

function updateTotal(price) {
    var people = parseInt(document.getElementById('bookPeople').value) || 1;
    var total  = price * people;
    document.getElementById('bookTotal').textContent = 'NPR ' + total.toLocaleString();
}

// Book form validation
function bindBookForm() {
    var form = document.getElementById('bookForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        var date = document.getElementById('bookDate').value;
        if (!date) {
            e.preventDefault();
            alert('Please select an adventure date.');
        }
    });
}

// ── Language Toggle Event Listener ────────────────────────────────
window.addEventListener('languagechange', function () {
    setGreeting();
    setLiveDate();
});
