/* dashboard_Admin.js — Thrill Sphere Admin Dashboard Logic */

(function () {
    'use strict';

    // ── Global State Cache ────────────────────────────────────────────────
    let state = {
        currentTab: 'overview',
        activities: {}, // key: val
        bookings: [],
        payments: [],
        users: [],
        auditLogs: [],
        selectedCalDate: null,
        calMonth: new Date().getMonth(),
        calYear: new Date().getFullYear(),
        charts: {}
    };

    // ── DOM References ────────────────────────────────────────────────────
    const refs = {
        pageTitle: document.getElementById('page-title'),
        pageSubtitle: document.getElementById('page-subtitle'),
        currentDateSpan: document.getElementById('current-date'),
        alertContainer: document.getElementById('alertContainer'),
        
        // Modals
        activityModal: document.getElementById('activityModal'),
        activityForm: document.getElementById('activityForm'),
        bookingModal: document.getElementById('bookingModal'),
        bookingForm: document.getElementById('bookingForm'),
        userModal: document.getElementById('userModal'),
        userForm: document.getElementById('userForm'),
        duplicateModal: document.getElementById('duplicateModal'),
        duplicateForm: document.getElementById('duplicateForm'),

        // Calendar
        adminCalMonthYear: document.getElementById('adminCalMonthYear'),
        adminCalGrid: document.getElementById('adminCalGrid'),
        adminCalDetailsList: document.getElementById('adminCalDetailsList'),
        adminCalSelectedDate: document.getElementById('adminCalSelectedDate')
    };

    // ── Boot ──────────────────────────────────────────────────────────────
    function init() {
        // Set date in header
        refs.currentDateSpan.textContent = new Date().toLocaleDateString('en-US', {
            weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
        });

        // Initialize state activities from server-injected window variable
        if (window.THRILL_ACTIVITIES) {
            state.activities = window.THRILL_ACTIVITIES;
        }

        // Add calendar events
        document.getElementById('adminCalPrev').addEventListener('click', () => adjustCalMonth(-1));
        document.getElementById('adminCalNext').addEventListener('click', () => adjustCalMonth(1));

        // Initial fetch
        loadDashboardData(true);

        // Auto refresh stats every 30s
        setInterval(() => loadDashboardData(false), 30000);
    }

    // ── Flash Alerts ──────────────────────────────────────────────────────
    function showAlert(message, type = 'success') {
        const alert = document.createElement('div');
        alert.className = `alert-box alert-${type}`;
        alert.innerHTML = `<i class="bx bx-${type === 'success' ? 'check-circle' : 'error-circle'}"></i> <span>${message}</span>`;
        refs.alertContainer.appendChild(alert);
        
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    }

    // ── Data Loading & API Calls ──────────────────────────────────────────
    // ── Loading progress bar ──────────────────────────────────────────────
    function showLoadingBar(visible) {
        let bar = document.getElementById('adminLoadingBar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'adminLoadingBar';
            bar.style.cssText = [
                'position:fixed','top:0','left:0','right:0','height:3px',
                'background:linear-gradient(90deg,#6366f1 0%,#a78bfa 50%,#6366f1 100%)',
                'background-size:200% 100%',
                'z-index:99999','transition:opacity 0.4s ease',
                'animation:adminBarShimmer 1.2s linear infinite'
            ].join(';');
            const st = document.createElement('style');
            st.textContent = '@keyframes adminBarShimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}';
            document.head.appendChild(st);
            document.body.appendChild(bar);
        }
        bar.style.opacity = visible ? '1' : '0';
    }

    function loadDashboardData(firstLoad = false) {
        showLoadingBar(true);
        // Run fetches in parallel
        Promise.all([
            fetch('/admin/api/activities').then(res => res.json()),
            fetch('/admin/api/bookings').then(res => res.json()),
            fetch('/admin/api/users').then(res => res.json()),
            fetch('/admin/api/payments').then(res => res.json()),
            fetch('/admin/api/audit-logs').then(res => res.json())
        ]).then(([activities, bookings, users, payments, auditLogs]) => {
            // Update activities cache
            state.activities = {};
            activities.forEach(a => { state.activities[a.id] = a; });

            state.bookings = bookings;
            state.users = users;
            state.payments = payments;
            state.auditLogs = auditLogs;

            // Render current view
            renderCurrentView(firstLoad);
            showLoadingBar(false);
        }).catch(err => {
            showLoadingBar(false);
            console.error('[API Load Error]:', err);
            showAlert('Failed to refresh data from server', 'danger');
        });
    }

    function renderCurrentView(firstLoad) {
        // Redraw based on current active tab
        renderOverviewDashboard(firstLoad);
        populateFilterDropdowns();
        renderBookingsTable();
        renderActivitiesGrid();
        renderPaymentsTable();
        renderUsersTable();
        renderAuditLogsTable();
        renderNotificationForm();
        renderCalendarGrid();
    }

    // ── SPA Tab Router ─────────────────────────────────────────────────────
    window.switchAdminTab = function (tabName, el) {
        state.currentTab = tabName;

        // Update active sidebar link
        document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        if (el) {
            el.classList.add('active');
        } else {
            // Fallback: locate matching link
            const links = document.querySelectorAll('.sidebar-nav .nav-link');
            links.forEach(l => {
                if (l.textContent.toLowerCase().includes(tabName)) {
                    l.classList.add('active');
                }
            });
        }

        // Update titles
        const titles = {
            'overview': { title: 'Dashboard Overview', sub: 'Welcome back to the command center' },
            'activities': { title: 'Manage Activities', sub: 'Configure and publish adventure activities' },
            'bookings': { title: 'Customer Bookings', sub: 'Audit registrations, schedule updates, and notes' },
            'payments': { title: 'Payment Audits', sub: 'Verify QR codes, process refunds, and generate reports' },
            'users': { title: 'User Accounts', sub: 'Manage permissions, review spending, and suspend users' },
            'calendar': { title: 'Activity Planner', sub: 'Color-coded slot availability and booking transfers' },
            'notifications': { title: 'Notification Dispatcher', sub: 'Broadcast messages to customer dashboard feeds' },
            'audit-logs': { title: 'Audit Trail Logs', sub: 'Chronological list of admin and security actions' }
        };

        const pageInfo = titles[tabName] || { title: 'Admin Controls', sub: '' };
        refs.pageTitle.textContent = pageInfo.title;
        refs.pageSubtitle.textContent = pageInfo.sub;

        // Toggle active sections
        document.querySelectorAll('.admin-section').forEach(sec => {
            sec.classList.remove('active');
        });
        const activeSec = document.getElementById(`sec-${tabName}`);
        if (activeSec) {
            activeSec.classList.add('active');
        }

        // Trigger updates specific to tab
        if (tabName === 'overview') {
            loadDashboardData(true);
        } else {
            loadDashboardData(false);
        }
    };

    // ── TAB 1: OVERVIEW & CHARTS ──────────────────────────────────────────
    function renderOverviewDashboard(firstLoad) {
        // Populate recent bookings table
        const tbody = document.querySelector('#recentBookingsTable tbody');
        tbody.innerHTML = '';
        state.bookings.slice(0, 5).forEach(b => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${b.id}</td>
                <td><strong>${escapeHTML(b.user_name)}</strong><br><small class="text-secondary">${escapeHTML(b.user_email)}</small></td>
                <td>${escapeHTML(b.activity)}</td>
                <td>${formatDate(b.date)}</td>
                <td>NPR ${b.total.toLocaleString()}</td>
                <td><span class="badge badge-${b.status}">${b.status}</span></td>
            `;
            tbody.appendChild(tr);
        });

        // Populate recent audit logs list
        const auditList = document.getElementById('recentAuditList');
        auditList.innerHTML = '';
        state.auditLogs.slice(0, 5).forEach(log => {
            const item = document.createElement('div');
            item.className = 'audit-item';
            item.innerHTML = `
                <div class="audit-item-header">
                    <span>${escapeHTML(log.admin_name || 'System')} &middot; ${escapeHTML(log.action)}</span>
                    <span class="audit-time">${new Date(log.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="text-secondary">${escapeHTML(log.target_record)} &mdash; ${escapeHTML(log.details)}</div>
            `;
            auditList.appendChild(item);
        });

        // Initialize Charts if first load or canvas redraw
        if (firstLoad) {
            initCharts();
        }
    }

    function initCharts() {
        // Destroy existing
        if (state.charts.revenue) state.charts.revenue.destroy();
        if (state.charts.popularity) state.charts.popularity.destroy();

        // 1. Process Revenue Chart Data (last 7 bookings/days)
        const dailyRevenue = {};
        state.bookings.forEach(b => {
            if (b.payment_status === 'confirmed' && b.status !== 'cancelled') {
                const day = b.date;
                dailyRevenue[day] = (dailyRevenue[day] || 0) + b.total;
            }
        });
        const revLabels = Object.keys(dailyRevenue).sort().slice(-7);
        const revValues = revLabels.map(l => dailyRevenue[l]);

        const revCtx = document.getElementById('revenueChart').getContext('2d');
        state.charts.revenue = new Chart(revCtx, {
            type: 'line',
            data: {
                labels: revLabels.map(l => formatDateShort(l)),
                datasets: [{
                    label: 'Revenue (NPR)',
                    data: revValues,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // 2. Process Activity Popularity Chart Data
        const popularity = {};
        state.bookings.forEach(b => {
            if (b.status !== 'cancelled') {
                popularity[b.activity] = (popularity[b.activity] || 0) + b.people;
            }
        });
        const popLabels = Object.keys(popularity);
        const popValues = popLabels.map(l => popularity[l]);

        const popCtx = document.getElementById('popularityChart').getContext('2d');
        state.charts.popularity = new Chart(popCtx, {
            type: 'doughnut',
            data: {
                labels: popLabels,
                datasets: [{
                    data: popValues,
                    backgroundColor: [
                        '#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#ec4899', '#8b5cf6', '#06b6d4'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', boxWidth: 12, font: { family: 'Plus Jakarta Sans' } }
                    }
                }
            }
        });
    }

    // ── TAB 2: ACTIVITIES ─────────────────────────────────────────────────
    function renderActivitiesGrid() {
        const container = document.getElementById('activitiesContainer');
        container.innerHTML = '';

        Object.values(state.activities).forEach(act => {
            if (act.status === 'archived') return;

            const card = document.createElement('div');
            card.className = `activity-card ${act.status === 'disabled' ? 'opacity-60' : ''}`;
            card.innerHTML = `
                <div class="activity-media">
                    <img src="/static/images/${act.pic || 'Trekking_Pic.jpeg'}" alt="${escapeHTML(act.name)}">
                    <div class="activity-icon-badge">
                        <img src="/static/images/${act.img || 'Mountain-Main.png'}" alt="Icon">
                    </div>
                </div>
                <div class="activity-body">
                    <h3>${escapeHTML(act.name)}</h3>
                    <p>${escapeHTML(act.description || 'No description provided.')}</p>
                    <div class="activity-meta">
                        <span><i class="bx bx-map"></i> ${escapeHTML(act.location)}</span>
                        <span><i class="bx bx-time"></i> ${escapeHTML(act.duration)}</span>
                        <span><strong>NPR ${act.price.toLocaleString()}</strong></span>
                    </div>
                    <div class="activity-actions">
                        ${window.THRILL_ADMIN_ROLE !== 'staff' ? `
                            <button class="btn btn-secondary btn-sm" onclick="openActivityModal('edit', '${act.id}')"><i class="bx bx-edit"></i> Edit</button>
                            <button class="btn btn-secondary btn-sm" onclick="openDuplicateModal('${act.id}')"><i class="bx bx-copy"></i> Clone</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteActivity('${act.id}')"><i class="bx bx-archive"></i> Archive</button>
                        ` : `
                            <button class="btn btn-secondary btn-sm" disabled><i class="bx bx-lock"></i> Staff View Only</button>
                        `}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    window.filterActivities = function () {
        const q = document.getElementById('activitySearchInput').value.toLowerCase();
        document.querySelectorAll('.activity-card').forEach(card => {
            const h3 = card.querySelector('h3').textContent.toLowerCase();
            const p = card.querySelector('p').textContent.toLowerCase();
            if (h3.includes(q) || p.includes(q)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    };

    window.deleteActivity = function (id) {
        if (!confirm('Are you sure you want to archive this activity? This will disable scheduling new slots for users.')) return;
        
        fetch(`/admin/api/activities/${id}`, {
            method: 'DELETE'
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Activity archived successfully');
                loadDashboardData();
            } else {
                showAlert(data.message || 'Failed to archive activity', 'danger');
            }
        });
    };

    // ── TAB 3: BOOKINGS ───────────────────────────────────────────────────
    function populateFilterDropdowns() {
        const select = document.getElementById('filterActivity');
        const currentVal = select.value;
        select.innerHTML = '<option value="">All Activities</option>';
        Object.values(state.activities).forEach(a => {
            if (a.status !== 'archived') {
                const opt = document.createElement('option');
                opt.value = a.name;
                opt.textContent = a.name;
                select.appendChild(opt);
            }
        });
        select.value = currentVal;
    }

    function renderBookingsTable() {
        const tbody = document.querySelector('#mainBookingsTable tbody');
        tbody.innerHTML = '';

        state.bookings.forEach(b => {
            const tr = document.createElement('tr');
            tr.className = 'booking-row-item';
            tr.innerHTML = `
                <td>#${b.id}</td>
                <td>
                    <strong>${escapeHTML(b.user_name)}</strong><br>
                    <small class="text-secondary">${escapeHTML(b.user_email)}</small>
                </td>
                <td>${escapeHTML(b.activity)}</td>
                <td>${formatDate(b.date)}</td>
                <td>${b.people}</td>
                <td>NPR ${b.total.toLocaleString()}</td>
                <td><span class="badge badge-${b.status}">${b.status}</span></td>
                <td><span class="badge badge-${b.payment_status || 'confirmed'}">${b.payment_status || 'confirmed'}</span></td>
                <td><small class="text-secondary">${escapeHTML(b.txn_code || '—')}</small></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="openBookingModal(${JSON.stringify(b).replace(/"/g, '&quot;')})">
                        <i class="bx bx-edit"></i> Manage
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.filterBookingsTable = function () {
        const query = document.getElementById('bookingSearchInput').value.toLowerCase();
        const activity = document.getElementById('filterActivity').value;
        const bookingStatus = document.getElementById('filterBookingStatus').value;
        const paymentStatus = document.getElementById('filterPaymentStatus').value;

        document.querySelectorAll('#mainBookingsTable tbody tr').forEach((tr, i) => {
            const b = state.bookings[i];
            if (!b) return;

            const nameMatches = b.user_name.toLowerCase().includes(query) || b.user_email.toLowerCase().includes(query) || String(b.id).includes(query);
            const actMatches = !activity || b.activity === activity;
            const bStatMatches = !bookingStatus || b.status === bookingStatus;
            const pStatMatches = !paymentStatus || (b.payment_status || 'confirmed') === paymentStatus;

            if (nameMatches && actMatches && bStatMatches && pStatMatches) {
                tr.style.display = '';
            } else {
                tr.style.display = 'none';
            }
        });
    };

    // ── TAB 4: PAYMENTS ───────────────────────────────────────────────────
    function renderPaymentsTable() {
        const tbody = document.querySelector('#paymentsTable tbody');
        tbody.innerHTML = '';

        // Calculate statistics
        let revenueToday = 0;
        let revenueMonth = 0;
        let pendingCount = 0;

        const todayStr = new Date().toISOString().split('T')[0];
        const currentMonth = new Date().toISOString().substring(0, 7); // YYYY-MM

        state.payments.forEach(p => {
            if (p.payment_status === 'confirmed') {
                if (p.date === todayStr) {
                    revenueToday += p.total;
                }
                if (p.date.substring(0, 7) === currentMonth) {
                    revenueMonth += p.total;
                }
            } else if (p.payment_status === 'pending') {
                pendingCount++;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${p.booking_id}</td>
                <td><strong>${escapeHTML(p.user_name)}</strong><br><small class="text-secondary">${escapeHTML(p.user_email)}</small></td>
                <td>${escapeHTML(p.activity)}</td>
                <td>${formatDate(p.date)}</td>
                <td>NPR ${p.total.toLocaleString()}</td>
                <td><span class="role-badge">${p.payment_method || 'QR'}</span></td>
                <td><code>${escapeHTML(p.txn_code || '—')}</code></td>
                <td><span class="badge badge-${p.payment_status || 'confirmed'}">${p.payment_status || 'confirmed'}</span></td>
                <td>
                    ${p.payment_status === 'pending' ? `
                        <button class="btn btn-primary btn-sm" onclick="verifyPayment(${p.booking_id})"><i class="bx bx-check"></i> Verify</button>
                    ` : ''}
                    ${p.payment_status !== 'refunded' && window.THRILL_ADMIN_ROLE !== 'staff' ? `
                        <button class="btn btn-danger btn-sm" onclick="refundPayment(${p.booking_id})"><i class="bx bx-undo"></i> Refund</button>
                    ` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Set metrics
        document.getElementById('stat-revenue-today').textContent = `NPR ${revenueToday.toLocaleString()}`;
        document.getElementById('stat-revenue-month').textContent = `NPR ${revenueMonth.toLocaleString()}`;
        document.getElementById('stat-pending-payments').textContent = pendingCount;
    }

    window.filterPaymentsTable = function () {
        const q = document.getElementById('paymentSearchInput').value.toLowerCase();
        document.querySelectorAll('#paymentsTable tbody tr').forEach((tr, i) => {
            const p = state.payments[i];
            if (!p) return;
            const searchStr = `${p.user_name} ${p.user_email} ${p.activity} ${p.txn_code || ''} ${p.booking_id}`.toLowerCase();
            tr.style.display = searchStr.includes(q) ? '' : 'none';
        });
    };

    window.verifyPayment = function (bookingId) {
        if (!confirm('Verify this payment reference code?')) return;
        fetch('/admin/api/payments/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({ booking_id: bookingId })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Payment verified successfully');
                loadDashboardData();
            } else {
                showAlert(data.message || 'Failed to verify payment', 'danger');
            }
        });
    };

    window.refundPayment = function (bookingId) {
        if (!confirm('Are you sure you want to refund this payment? This will issue NPR refund and cancel the booking slots.')) return;
        fetch('/admin/api/payments/refund', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({ booking_id: bookingId })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Refund processed and booking cancelled');
                loadDashboardData();
            } else {
                showAlert(data.message || 'Refund failed', 'danger');
            }
        });
    };

    window.exportPayments = function (format) {
        if (state.payments.length === 0) {
            showAlert('No transactions available to export', 'danger');
            return;
        }

        const dateStr = new Date().toISOString().split('T')[0];
        const headers = ['Booking ID', 'Customer Name', 'Customer Email', 'Activity', 'Date', 'Amount (NPR)', 'Method', 'Txn Code', 'Status'];
        const rows = state.payments.map(p => [
            p.booking_id,
            p.user_name,
            p.user_email,
            p.activity,
            p.date,
            p.total,
            p.payment_method || 'QR',
            p.txn_code || '',
            p.payment_status
        ]);

        if (format === 'csv') {
            const csvContent = [
                headers.join(','),
                ...rows.map(r => r.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
            ].join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.setAttribute('download', `thrilldash_revenue_${dateStr}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showAlert('Revenue report exported as CSV');
            return;
        }

        if (format === 'excel') {
            // Build a proper Excel XML Spreadsheet (SpreadsheetML) — opens natively in Excel/Sheets
            const xmlRows = [headers, ...rows].map(row =>
                '<Row>' + row.map(cell => {
                    const isNum = typeof cell === 'number' || (!isNaN(cell) && cell !== '');
                    return isNum
                        ? `<Cell><Data ss:Type="Number">${cell}</Data></Cell>`
                        : `<Cell><Data ss:Type="String">${String(cell).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</Data></Cell>`;
                }).join('') + '</Row>'
            ).join('\n');

            const xlsContent = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Styles>
  <Style ss:ID="Header"><Font ss:Bold="1"/></Style>
 </Styles>
 <Worksheet ss:Name="Revenue Report">
  <Table>
   ${xmlRows}
  </Table>
 </Worksheet>
</Workbook>`;
            const blob = new Blob([xlsContent], { type: 'application/vnd.ms-excel;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.setAttribute('download', `thrilldash_revenue_${dateStr}.xls`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showAlert('Revenue report exported as Excel');
            return;
        }

        if (format === 'pdf') {
            // Build a clean printable HTML page and trigger browser print-to-PDF
            const totalRevenue = state.payments
                .filter(p => p.payment_status === 'confirmed')
                .reduce((sum, p) => sum + (p.total || 0), 0);

            const tableRows = rows.map(r =>
                `<tr>${r.map((cell, i) => {
                    if (i === 8) { // Status column — add color
                        const color = cell === 'confirmed' ? '#10b981' : cell === 'refunded' ? '#ef4444' : '#f59e0b';
                        return `<td><span style="color:${color};font-weight:600">${cell}</span></td>`;
                    }
                    if (i === 5) return `<td style="text-align:right">NPR ${Number(cell).toLocaleString()}</td>`;
                    return `<td>${cell}</td>`;
                }).join('')}</tr>`
            ).join('\n');

            const pdfHtml = `<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>ThrillDash Revenue Report — ${dateStr}</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Segoe UI', Arial, sans-serif; padding: 32px; color: #111; }
  h1 { font-size: 22px; margin-bottom: 4px; color: #1a1a2e; }
  .subtitle { color: #666; font-size: 13px; margin-bottom: 24px; }
  .summary { display: flex; gap: 24px; margin-bottom: 28px; }
  .stat { background: #f4f4f8; border-radius: 10px; padding: 14px 20px; }
  .stat-label { font-size: 12px; color: #888; }
  .stat-value { font-size: 20px; font-weight: 700; color: #4f46e5; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { background: #1a1a2e; color: #fff; padding: 10px 12px; text-align: left; }
  td { padding: 9px 12px; border-bottom: 1px solid #eee; }
  tr:nth-child(even) td { background: #f9f9fb; }
  .footer { margin-top: 24px; font-size: 11px; color: #aaa; text-align: center; }
  @media print { body { padding: 16px; } }
</style>
</head><body>
<h1>🏔 ThrillDash — Revenue Report</h1>
<div class="subtitle">Generated on ${new Date().toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'})}</div>
<div class="summary">
  <div class="stat"><div class="stat-label">Total Transactions</div><div class="stat-value">${state.payments.length}</div></div>
  <div class="stat"><div class="stat-label">Confirmed Revenue</div><div class="stat-value">NPR ${totalRevenue.toLocaleString()}</div></div>
  <div class="stat"><div class="stat-label">Pending Payments</div><div class="stat-value">${state.payments.filter(p=>p.payment_status==='pending').length}</div></div>
</div>
<table>
<thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead>
<tbody>${tableRows}</tbody>
</table>
<div class="footer">Confidential — ThrillDash Admin Portal &mdash; ${dateStr}</div>
</body></html>`;

            const printWin = window.open('', '_blank', 'width=900,height=700');
            printWin.document.write(pdfHtml);
            printWin.document.close();
            printWin.focus();
            // Small delay ensures styles are applied before print dialog
            setTimeout(() => { printWin.print(); }, 400);
            showAlert('PDF print dialog opened — use "Save as PDF" in your print settings');
            return;
        }
    };

    // ── TAB 5: USERS ──────────────────────────────────────────────────────
    function renderUsersTable() {
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = '';

        state.users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${u.id}</td>
                <td><strong>${escapeHTML(u.name)}</strong></td>
                <td>${escapeHTML(u.email)}</td>
                <td><span class="role-badge">${u.role}</span></td>
                <td><span class="badge badge-${u.status || 'active'}">${u.status || 'active'}</span></td>
                <td>${u.bookings_count || 0}</td>
                <td>NPR ${(u.total_spent || 0).toLocaleString()}</td>
                <td>${formatDate(u.created_at)}</td>
                <td>
                    ${window.THRILL_ADMIN_ROLE !== 'staff' && u.id !== window.THRILL_ADMIN_ID ? `
                        <button class="btn btn-secondary btn-sm" onclick="openUserModal(${JSON.stringify(u).replace(/"/g, '&quot;')})"><i class="bx bx-edit"></i> Edit</button>
                        ${u.status !== 'suspended' ? `
                            <button class="btn btn-danger btn-sm" onclick="toggleUserSuspend(${u.id}, 'suspend')">Suspend</button>
                        ` : `
                            <button class="btn btn-primary btn-sm" onclick="toggleUserSuspend(${u.id}, 'active')">Activate</button>
                        `}
                        ${window.THRILL_ADMIN_ROLE === 'super_admin' ? `
                            <button class="btn btn-danger btn-sm btn-icon" onclick="deleteUser(${u.id})"><i class="bx bx-trash"></i></button>
                        ` : ''}
                    ` : '<small class="text-secondary">—</small>'}
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Also update dispatcher dropdown
        const select = document.getElementById('notifUserSelect');
        const currentVal = select.value;
        select.innerHTML = '<option value="">-- Choose User --</option>';
        state.users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.id;
            opt.textContent = `${u.name} (${u.email})`;
            select.appendChild(opt);
        });
        select.value = currentVal;
    }

    window.filterUsersTable = function () {
        const q = document.getElementById('userSearchInput').value.toLowerCase();
        document.querySelectorAll('#usersTable tbody tr').forEach((tr, i) => {
            const u = state.users[i];
            if (!u) return;
            const searchStr = `${u.name} ${u.email} ${u.id}`.toLowerCase();
            tr.style.display = searchStr.includes(q) ? '' : 'none';
        });
    };

    window.toggleUserSuspend = function (userId, mode) {
        if (!confirm(`Are you sure you want to ${mode} this account? Suspended accounts cannot authenticate.`)) return;
        const targetUser = state.users.find(u => u.id === userId);
        if (!targetUser) return;

        fetch(`/admin/api/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({
                name: targetUser.name,
                email: targetUser.email,
                role: targetUser.role,
                status: mode === 'suspend' ? 'suspended' : 'active'
            })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert(`Account successfully marked: ${mode}`);
                loadDashboardData();
            } else {
                showAlert(data.message || 'Action failed', 'danger');
            }
        });
    };

    window.deleteUser = function (userId) {
        if (!confirm('WARNING: Permanently deleting this customer account will remove all their personal bookings and reports. Proceed?')) return;
        fetch(`/admin/api/users/${userId}`, {
            method: 'DELETE'
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('User account deleted permanently');
                loadDashboardData();
            } else {
                showAlert(data.message || 'Deletion failed', 'danger');
            }
        });
    };

    // ── TAB 6: EVENT PLANNER & CALENDAR ────────────────────────────────────
    function adjustCalMonth(dir) {
        state.calMonth += dir;
        if (state.calMonth < 0) {
            state.calMonth = 11;
            state.calYear--;
        } else if (state.calMonth > 11) {
            state.calMonth = 0;
            state.calYear++;
        }
        renderCalendarGrid();
    }

    function renderCalendarGrid() {
        const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        refs.adminCalMonthYear.textContent = `${months[state.calMonth]} ${state.calYear}`;

        // Compute slot booking states grouped by date
        const slotsByDate = {}; // 'YYYY-MM-DD': { 'activity': count }
        state.bookings.forEach(b => {
            if (b.status !== 'cancelled') {
                const d = b.date;
                if (!slotsByDate[d]) slotsByDate[d] = {};
                slotsByDate[d][b.activity] = (slotsByDate[d][b.activity] || 0) + b.people;
            }
        });

        // Get calendar grid
        const grid = refs.adminCalGrid;
        grid.innerHTML = '';

        // Add headers
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        days.forEach(d => {
            const el = document.createElement('div');
            el.className = 'cal-day-header';
            el.textContent = d;
            grid.appendChild(el);
        });

        // Build days grid
        const firstDay = new Date(state.calYear, state.calMonth, 1).getDay();
        const numDays = new Date(state.calYear, state.calMonth + 1, 0).getDate();
        const prevMonthNumDays = new Date(state.calYear, state.calMonth, 0).getDate();

        // Previous month bleed
        for (let i = firstDay - 1; i >= 0; i--) {
            const val = prevMonthNumDays - i;
            const cell = document.createElement('div');
            cell.className = 'cal-cell other-month';
            cell.innerHTML = `<span class="cal-num">${val}</span>`;
            grid.appendChild(cell);
        }

        // Active month days
        for (let day = 1; day <= numDays; day++) {
            const dateStr = `${state.calYear}-${String(state.calMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const cell = document.createElement('div');
            cell.className = 'cal-cell';
            if (state.selectedCalDate === dateStr) {
                cell.classList.add('selected');
            }

            const dayBookings = slotsByDate[dateStr] || {};
            
            // Build indicators color
            let indicatorHTML = '';
            let totalParticipantsOnDay = 0;
            let totalCapacityLimit = 0;

            Object.entries(dayBookings).forEach(([actName, booked]) => {
                // Find capacity
                let cap = 20;
                const actObj = Object.values(state.activities).find(a => a.name === actName);
                if (actObj) {
                    cap = actObj.capacity;
                }

                totalParticipantsOnDay += booked;
                totalCapacityLimit += cap;
            });

            // Set color dot status
            let dotColor = 'bg-gray'; // gray if no bookings
            if (totalParticipantsOnDay > 0) {
                const fillRatio = totalParticipantsOnDay / (totalCapacityLimit || 1);
                dotColor = fillRatio >= 1.0 ? 'bg-danger' : (fillRatio >= 0.7 ? 'bg-warning' : 'bg-success');
            }

            cell.innerHTML = `
                <span class="cal-num">${day}</span>
                <div class="cal-indicators">
                    <span class="cal-dot ${dotColor}"></span>
                    ${totalParticipantsOnDay > 0 ? `<small class="text-secondary" style="font-size:10px;">(${totalParticipantsOnDay})</small>` : ''}
                </div>
            `;

            cell.addEventListener('click', () => {
                state.selectedCalDate = dateStr;
                document.querySelectorAll('.cal-cell').forEach(c => c.classList.remove('selected'));
                cell.classList.add('selected');
                renderCalendarDetailsPanel(dateStr);
            });

            grid.appendChild(cell);
        }

        // Re-open details if date previously selected
        if (state.selectedCalDate) {
            renderCalendarDetailsPanel(state.selectedCalDate);
        }
    }

    function renderCalendarDetailsPanel(dateStr) {
        refs.adminCalSelectedDate.textContent = formatDate(dateStr);
        const panel = refs.adminCalDetailsList;
        panel.innerHTML = '';

        // Filter bookings on this date
        const dayBookings = state.bookings.filter(b => b.date === dateStr && b.status !== 'cancelled');

        // Group active activities
        const activeActs = Object.values(state.activities).filter(a => a.status === 'active');
        
        if (activeActs.length === 0) {
            panel.innerHTML = '<p class="text-secondary">No active activities configured.</p>';
            return;
        }

        activeActs.forEach(act => {
            const bookedForAct = dayBookings.filter(b => b.activity === act.name);
            const totalBooked = bookedForAct.reduce((sum, b) => sum + b.people, 0);
            const remaining = Math.max(0, act.capacity - totalBooked);

            const div = document.createElement('div');
            div.className = 'cal-slot-item';
            
            // Check status percentage
            const fillPct = Math.round((totalBooked / act.capacity) * 100);
            
            div.innerHTML = `
                <div class="cal-slot-header">
                    <span>${escapeHTML(act.name)}</span>
                    <span class="text-secondary" style="font-size:12px;">Cap: ${act.capacity}</span>
                </div>
                <div class="cal-slot-meta">
                    <span>Booked: <strong>${totalBooked} slots</strong></span>
                    <span>Remaining: <strong class="${remaining === 0 ? 'text-rose' : 'text-emerald'}">${remaining}</strong></span>
                </div>
                
                <!-- Capacity Bar -->
                <div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px; overflow:hidden; margin-bottom:12px;">
                    <div style="width:${Math.min(100, fillPct)}%; height:100%; background:${fillPct >= 100 ? 'var(--danger)' : (fillPct >= 70 ? 'var(--warning)' : 'var(--success)')};"></div>
                </div>

                <div class="cal-slot-bookings-list">
                    ${bookedForAct.length > 0 ? bookedForAct.map(b => `
                        <div class="cal-booking-mini">
                            <span>#${b.id} &middot; ${escapeHTML(b.user_name)} (x${b.people})</span>
                            <button class="btn btn-secondary btn-sm" style="padding:2px 6px; font-size:10px;" onclick="moveBookingShortcut(${b.id}, '${dateStr}')">Move</button>
                        </div>
                    `).join('') : '<small class="text-secondary">No bookings scheduled.</small>'}
                </div>
            `;
            panel.appendChild(div);
        });
    }

    window.moveBookingShortcut = function(bookingId, currentDate) {
        const targetDate = prompt('Enter the new booking date (format: YYYY-MM-DD):', currentDate);
        if (!targetDate) return;
        
        // Simple regex check
        if (!/^\d{4}-\d{2}-\d{2}$/.test(targetDate)) {
            alert('Invalid date format. Use YYYY-MM-DD');
            return;
        }

        const b = state.bookings.find(bk => bk.id === bookingId);
        if (!b) return;

        // Perform API PUT call
        fetch(`/admin/api/bookings/${bookingId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({
                status: b.status,
                payment_status: b.payment_status || 'confirmed',
                internal_notes: b.internal_notes || '',
                date: targetDate,
                people: b.people,
                price: b.price
            })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Booking date updated and rescheduled successfully');
                loadDashboardData();
            } else {
                showAlert(data.message || 'Transfer failed', 'danger');
            }
        });
    };

    // ── TAB 7: NOTIFICATIONS ──────────────────────────────────────────────
    function renderNotificationForm() {
        // Form layout rendered statically in html, state verified here
    }

    window.dispatchNotification = function (e) {
        e.preventDefault();
        const userId = document.getElementById('notifUserSelect').value;
        const title = document.getElementById('notifTitle').value.trim();
        const msg = document.getElementById('notifMessage').value.trim();

        if (!userId || !title || !msg) {
            showAlert('Please populate all notification fields', 'danger');
            return;
        }

        fetch('/admin/api/notifications', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({ user_id: userId, title: title, message: msg })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Notification broadcast successfully to customer dashboard');
                document.getElementById('notificationForm').reset();
            } else {
                showAlert(data.message || 'Dispatch failed', 'danger');
            }
        });
    };

    // ── TAB 8: AUDIT LOGS ─────────────────────────────────────────────────
    function renderAuditLogsTable() {
        const tbody = document.querySelector('#auditLogsTable tbody');
        tbody.innerHTML = '';

        state.auditLogs.forEach(log => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatDateLong(log.timestamp)}</td>
                <td><strong>${escapeHTML(log.admin_name || 'System')}</strong></td>
                <td><span class="role-badge">${escapeHTML(log.action)}</span></td>
                <td><code>${escapeHTML(log.target_record)}</code></td>
                <td>${escapeHTML(log.details || '—')}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.filterAuditLogsTable = function () {
        const q = document.getElementById('auditSearchInput').value.toLowerCase();
        document.querySelectorAll('#auditLogsTable tbody tr').forEach((tr, i) => {
            const log = state.auditLogs[i];
            if (!log) return;
            const searchStr = `${log.admin_name || 'system'} ${log.action} ${log.target_record} ${log.details || ''}`.toLowerCase();
            tr.style.display = searchStr.includes(q) ? '' : 'none';
        });
    };

    // ── MODAL FORM SUBMISSIONS ────────────────────────────────────────────
    
    // Activity Form
    window.openActivityModal = function (mode = 'create', id = '') {
        refs.activityForm.reset();
        const modeInput = document.getElementById('actFormMode');
        const idInput = document.getElementById('actIdInput');
        const titleEl = document.getElementById('activityModalTitle');
        const statusGroup = document.getElementById('actStatusFormGroup');

        if (mode === 'edit' && id) {
            modeInput.value = 'edit';
            idInput.value = id;
            idInput.disabled = true; // cannot edit slug on modification
            titleEl.textContent = 'Edit Activity Config';
            statusGroup.style.display = 'block';

            // Populate form
            const act = state.activities[id];
            if (act) {
                document.getElementById('actNameInput').value = act.name;
                document.getElementById('actPriceInput').value = act.price;
                document.getElementById('actCapacityInput').value = act.capacity;
                document.getElementById('actLocationInput').value = act.location;
                document.getElementById('actDurationInput').value = act.duration;
                document.getElementById('actDifficultyInput').value = act.difficulty || 'Medium';
                document.getElementById('actCategoryInput').value = act.category || 'Adventure';
                document.getElementById('actDescInput').value = act.description || '';
                document.getElementById('actImgSelect').value = act.img || 'Mountain-Main.png';
                document.getElementById('actPicSelect').value = act.pic || 'Trekking_Pic.jpeg';
                document.getElementById('actDatesInput').value = act.available_dates || '';
                document.getElementById('actStatusInput').value = act.status || 'active';
            }
        } else {
            modeInput.value = 'create';
            idInput.value = '';
            idInput.disabled = false;
            titleEl.textContent = 'Create Dynamic Activity';
            statusGroup.style.display = 'none';
        }

        refs.activityModal.classList.add('active');
    };

    window.closeActivityModal = function () {
        refs.activityModal.classList.remove('active');
    };

    window.submitActivityForm = function (e) {
        e.preventDefault();
        const mode = document.getElementById('actFormMode').value;
        const id = document.getElementById('actIdInput').value.trim();
        
        const payload = {
            name: document.getElementById('actNameInput').value.trim(),
            price: parseFloat(document.getElementById('actPriceInput').value),
            capacity: parseInt(document.getElementById('actCapacityInput').value),
            location: document.getElementById('actLocationInput').value.trim(),
            duration: document.getElementById('actDurationInput').value.trim(),
            difficulty: document.getElementById('actDifficultyInput').value,
            category: document.getElementById('actCategoryInput').value.trim(),
            description: document.getElementById('actDescInput').value.trim(),
            img: document.getElementById('actImgSelect').value,
            pic: document.getElementById('actPicSelect').value,
            available_dates: document.getElementById('actDatesInput').value.trim()
        };

        let url = '/admin/api/activities';
        let method = 'POST';

        if (mode === 'edit') {
            url += `/${id}`;
            method = 'PUT';
            payload.status = document.getElementById('actStatusInput').value;
        } else {
            payload.id = id;
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert(`Activity ${mode === 'edit' ? 'updated' : 'created'} successfully`);
                closeActivityModal();
                loadDashboardData();
            } else {
                showAlert(data.message || 'Operation failed', 'danger');
            }
        });
    };

    // Booking Detail Form
    window.openBookingModal = function (booking) {
        refs.bookingForm.reset();
        document.getElementById('bkFormId').value = booking.id;
        document.getElementById('bkFormUserId').value = booking.user_id;

        document.getElementById('bkDetailName').textContent = booking.user_name || '—';
        document.getElementById('bkDetailEmail').textContent = booking.user_email || '—';
        document.getElementById('bkDetailActivity').value = booking.activity;
        document.getElementById('bkFormDate').value = booking.date;
        document.getElementById('bkFormPeople').value = booking.people;
        document.getElementById('bkFormPrice').value = booking.price;
        document.getElementById('bkDetailTotal').value = `NPR ${booking.total.toLocaleString()}`;
        document.getElementById('bkFormStatus').value = booking.status;
        document.getElementById('bkFormPaymentStatus').value = booking.payment_status || 'confirmed';
        document.getElementById('bkFormNotes').value = booking.internal_notes || '';

        // Dynamic total math on keypress
        const calcTotal = () => {
            const p = parseFloat(document.getElementById('bkFormPrice').value) || 0;
            const n = parseInt(document.getElementById('bkFormPeople').value) || 1;
            document.getElementById('bkDetailTotal').value = `NPR ${(p * n).toLocaleString()}`;
        };
        document.getElementById('bkFormPrice').oninput = calcTotal;
        document.getElementById('bkFormPeople').oninput = calcTotal;

        // Staff limitation checks
        if (window.THRILL_ADMIN_ROLE === 'staff') {
            document.getElementById('bkFormPaymentStatus').disabled = true; // Staff cannot refund or change payment status
        } else {
            document.getElementById('bkFormPaymentStatus').disabled = false;
        }

        refs.bookingModal.classList.add('active');
    };

    window.closeBookingModal = function () {
        refs.bookingModal.classList.remove('active');
    };

    window.submitBookingForm = function (e) {
        e.preventDefault();
        const id = document.getElementById('bkFormId').value;
        const payload = {
            date: document.getElementById('bkFormDate').value,
            people: parseInt(document.getElementById('bkFormPeople').value),
            price: parseFloat(document.getElementById('bkFormPrice').value),
            status: document.getElementById('bkFormStatus').value,
            payment_status: document.getElementById('bkFormPaymentStatus').value,
            internal_notes: document.getElementById('bkFormNotes').value.trim()
        };

        fetch(`/admin/api/bookings/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Booking metadata saved successfully');
                closeBookingModal();
                loadDashboardData();
            } else {
                showAlert(data.message || 'Operation failed', 'danger');
            }
        });
    };

    // User Form
    window.openUserModal = function (user) {
        refs.userForm.reset();
        document.getElementById('userFormId').value = user.id;
        document.getElementById('userFormName').value = user.name;
        document.getElementById('userFormEmail').value = user.email;
        document.getElementById('userFormRole').value = user.role;
        document.getElementById('userFormStatus').value = user.status || 'active';

        refs.userModal.classList.add('active');
    };

    window.closeUserModal = function () {
        refs.userModal.classList.remove('active');
    };

    window.submitUserForm = function (e) {
        e.preventDefault();
        const id = document.getElementById('userFormId').value;
        const payload = {
            name: document.getElementById('userFormName').value.trim(),
            email: document.getElementById('userFormEmail').value.trim(),
            role: document.getElementById('userFormRole').value,
            status: document.getElementById('userFormStatus').value
        };

        fetch(`/admin/api/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('User account configurations saved');
                closeUserModal();
                loadDashboardData();
            } else {
                showAlert(data.message || 'Failed to update user', 'danger');
            }
        });
    };

    // Activity Duplication
    window.openDuplicateModal = function(sourceId) {
        refs.duplicateForm.reset();
        document.getElementById('dupSourceId').value = sourceId;
        refs.duplicateModal.classList.add('active');
    };

    window.closeDuplicateModal = function() {
        refs.duplicateModal.classList.remove('active');
    };

    window.submitDuplicateForm = function(e) {
        e.preventDefault();
        const payload = {
            source_id: document.getElementById('dupSourceId').value,
            new_id: document.getElementById('dupNewId').value.trim(),
            new_name: document.getElementById('dupNewName').value.trim()
        };

        fetch('/admin/api/activities/duplicate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            if (data.success) {
                showAlert('Activity duplicated successfully');
                closeDuplicateModal();
                loadDashboardData();
            } else {
                showAlert(data.message || 'Duplication failed', 'danger');
            }
        });
    };


    // ── MANUAL PAYMENT MODAL ─────────────────────────────────────────────
    window.openManualPaymentModal = function () {
        document.getElementById('manualPaymentForm').reset();
        document.getElementById('manualPaymentModal').classList.add('active');
    };

    window.closeManualPaymentModal = function () {
        document.getElementById('manualPaymentModal').classList.remove('active');
    };

    window.submitManualPayment = function (e) {
        e.preventDefault();
        const bookingId = parseInt(document.getElementById('mpBookingId').value);
        const method    = document.getElementById('mpMethod').value;
        const txnRef    = document.getElementById('mpTxnRef').value.trim();

        if (!bookingId || bookingId < 1) {
            showAlert('Please enter a valid Booking ID', 'danger');
            return;
        }

        fetch('/admin/api/payments/manual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': window.CSRF_TOKEN || '' },
            body: JSON.stringify({ booking_id: bookingId, method, txn_code: txnRef })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showAlert('Manual payment recorded — booking confirmed & customer notified');
                closeManualPaymentModal();
                loadDashboardData();
            } else {
                showAlert(data.message || 'Failed to record payment', 'danger');
            }
        })
        .catch(() => showAlert('Network error — payment not recorded', 'danger'));
    };

    // Close manual payment modal on overlay click
    document.getElementById('manualPaymentModal')?.addEventListener('click', function (e) {
        if (e.target === this) closeManualPaymentModal();
    });

    // ── Helper Utilities ──────────────────────────────────────────────────
    function formatDate(dateStr) {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr;
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch (e) { return dateStr; }
    }

    function formatDateShort(dateStr) {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr;
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch (e) { return dateStr; }
    }

    function formatDateLong(dateStr) {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr;
            return d.toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: 'numeric', minute: '2-digit', second: '2-digit'
            });
        } catch (e) { return dateStr; }
    }

    function escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;');
    }

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
