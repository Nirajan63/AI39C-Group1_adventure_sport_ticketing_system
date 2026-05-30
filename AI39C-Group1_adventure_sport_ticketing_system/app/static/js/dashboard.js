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
    var g = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
    var el = document.getElementById('greeting');
    if (el) el.textContent = g;
}

// ── Live date ──────────────────────────────────────────────────────
function setLiveDate() {
    var el = document.getElementById('liveDate');
    if (!el) return;
    el.textContent = new Date().toLocaleDateString('en-US', {
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

// ── Cancel booking ─────────────────────────────────────────────────
function cancelBooking(bookingId, btn) {
    if (!confirm('Are you sure you want to cancel this booking? This cannot be undone.')) return;

    btn.disabled = true;
    btn.textContent = 'Cancelling…';

    var formData = new FormData();
    formData.append('booking_id', bookingId);

    fetch('/cancel-booking', {
        method: 'POST',
        body: formData
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.success) {
            // Update status badge
            var card = btn.closest('.booking-card');
            var badge = card.querySelector('.booking-status');
            badge.className = 'booking-status cancelled';
            badge.textContent = 'Cancelled';
            badge.setAttribute('data-status', 'cancelled');
            card.setAttribute('data-status', 'cancelled');

            // Remove cancel button
            btn.remove();

            // Dim the card slightly
            card.style.opacity = '0.65';
        } else {
            btn.disabled = false;
            btn.textContent = 'Cancel';
            alert(data.error || 'Could not cancel booking. Please try again.');
        }
    })
    .catch(function () {
        btn.disabled = false;
        btn.textContent = 'Cancel';
        alert('Network error. Please try again.');
    });
}
