// notifications.js — Real-time Client-side Notifications Manager

(function () {
    'use strict';

    let lastUnreadCount = 0;

    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (!response.ok) return;
            const notifications = await response.json();
            updateNotificationUI(notifications);
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    }

    function updateNotificationUI(notifications) {
        const unreadList = notifications.filter(n => n.status === 'unread');
        const unreadCount = unreadList.length;

        // 1. Update Bell Icon Dot & Badge
        const dot = document.querySelector('.notification-dot');
        if (dot) {
            if (unreadCount > 0) {
                dot.style.display = 'flex';
                dot.textContent = unreadCount;
                dot.classList.add('pulse-warning-dot');
            } else {
                dot.style.display = 'none';
                dot.textContent = '';
                dot.classList.remove('pulse-warning-dot');
            }
        }

        // 2. Play subtle sound or trigger visual pulse if new unread notification arrives
        if (unreadCount > lastUnreadCount) {
            // Trigger visual pulse on bell
            const bell = document.querySelector('.notification-button i');
            if (bell) {
                bell.classList.add('bx-tada');
                setTimeout(() => bell.classList.remove('bx-tada'), 1500);
            }
        }
        lastUnreadCount = unreadCount;

        // 3. Populate Header Dropdown
        const dropdownList = document.getElementById('notification-dropdown-list');
        if (dropdownList) {
            if (notifications.length === 0) {
                dropdownList.innerHTML = '<p class="menu-empty" style="text-align: center; padding: 15px 0;">No notifications yet.</p>';
            } else {
                dropdownList.innerHTML = notifications.map(n => `
                    <div class="dropdown-notification-item ${n.status === 'unread' ? 'unread' : ''}" 
                         style="padding: 10px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: start; gap: 8px; transition: background 0.2s; background: ${n.status === 'unread' ? 'rgba(99,102,241,0.03)' : 'transparent'};"
                         id="dropdown-notif-${n.id}">
                        <div style="flex-grow: 1; min-width: 0;">
                            <div style="font-weight: 600; font-size: 0.85rem; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHTML(n.title)}</div>
                            <div style="font-size: 0.75rem; color: var(--muted); margin-top: 2px; line-height: 1.4; word-break: break-word;">${escapeHTML(n.message)}</div>
                            <div style="font-size: 0.65rem; color: var(--muted); margin-top: 4px;">${formatTimeAgo(n.created_at)}</div>
                        </div>
                        ${n.status === 'unread' ? `
                            <button onclick="markSingleAsRead(${n.id}, event)" 
                                    style="background: none; border: none; cursor: pointer; color: var(--accent); padding: 2px; flex-shrink: 0;"
                                    title="Mark as read">
                                <i class="bx bx-check-circle" style="font-size: 1.1rem;"></i>
                            </button>
                        ` : ''}
                    </div>
                `).join('');
            }
        }

        // 4. Populate Customer Dashboard notifications list if user is on the dashboard
        const dashboardList = document.querySelector('.dash-section#notifications .notifications-list');
        if (dashboardList) {
            if (notifications.length === 0) {
                dashboardList.innerHTML = '<p>You have no notifications at this time.</p>';
            } else {
                dashboardList.innerHTML = notifications.map(n => `
                    <div class="notification-item ${n.status === 'unread' ? 'unread' : ''}" 
                         id="notif-${n.id}" 
                         style="padding: 16px; border-radius: 12px; border: 1px solid var(--border); background: ${n.status === 'unread' ? 'rgba(99,102,241,0.05)' : 'rgba(255,255,255,0.01)'}; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s; margin-bottom: 12px;">
                        <div style="flex-grow: 1; margin-right: 15px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <h4 style="margin: 0; font-size: 1rem; font-weight: 700; color: var(--text);">${escapeHTML(n.title)}</h4>
                                ${n.status === 'unread' ? '<span class="status-badge" style="background: var(--accent); color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;">NEW</span>' : ''}
                            </div>
                            <p style="margin: 6px 0 0; font-size: 0.9rem; color: var(--muted); line-height: 1.5;">${escapeHTML(n.message)}</p>
                            <span style="font-size: 0.75rem; color: var(--muted); margin-top: 8px; display: inline-block;">
                                <i class="bx bx-time-five" style="vertical-align: middle; margin-right: 2px;"></i> ${formatTimeAgo(n.created_at)}
                            </span>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center; flex-shrink: 0;">
                            ${n.status === 'unread' ? `
                                <button onclick="markSingleAsRead(${n.id}, event)" 
                                        class="btn btn-secondary btn-sm" 
                                        style="display: flex; align-items: center; gap: 4px; padding: 6px 12px; font-size: 0.8rem; background: var(--accent); color: #fff; border: none; border-radius: 6px; cursor: pointer;">
                                    <i class="bx bx-check"></i> Mark as Read
                                </button>
                            ` : `
                                <span style="font-size: 0.8rem; color: var(--muted);"><i class="bx bx-check-double"></i> Read</span>
                            `}
                        </div>
                    </div>
                `).join('');
            }

            // Also update Dashboard sidebar notifications badge if present
            const sideBadge = document.querySelector('.nav-item .notif-badge');
            if (sideBadge) {
                if (unreadCount > 0) {
                    sideBadge.style.display = 'inline-block';
                    sideBadge.textContent = unreadCount;
                } else {
                    sideBadge.style.display = 'none';
                }
            }
        }
    }

    // Mark single notification as read
    window.markSingleAsRead = async function (id, event) {
        if (event) event.stopPropagation();
        try {
            const res = await fetch('/read-notification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ id: id })
            });
            if (res.ok) {
                fetchNotifications();
            }
        } catch (e) {
            console.error('Error marking notification read:', e);
        }
    };

    // Mark all notifications as read
    window.markAllNotificationsAsRead = async function (event) {
        if (event) event.stopPropagation();
        if (!confirm('Mark all notifications as read?')) return;
        try {
            const res = await fetch('/api/notifications/read-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            if (res.ok) {
                fetchNotifications();
            }
        } catch (e) {
            console.error('Error marking all notifications read:', e);
        }
    };

    function getCsrfToken() {
        return window.CSRF_TOKEN || '';
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    function formatTimeAgo(dateStr) {
        if (!dateStr) return '';
        try {
            // Normalize space to T for ISO parser compliance
            const normalized = dateStr.replace(' ', 'T');
            const d = new Date(normalized);
            const diffMs = new Date() - d;
            const diffMins = Math.floor(diffMs / 60000);
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            const diffHours = Math.floor(diffMins / 60);
            if (diffHours < 24) return `${diffHours}h ago`;
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays}d ago`;
        } catch(e) {
            return dateStr;
        }
    }

    // Initial load and periodic polling (every 5 seconds)
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('.notification-wrap')) {
            fetchNotifications();
            setInterval(fetchNotifications, 5000);
        }
    });

})();
