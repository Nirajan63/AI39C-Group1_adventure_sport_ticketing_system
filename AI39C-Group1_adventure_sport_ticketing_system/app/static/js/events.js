// ================= EVENTS PAGE INTERACTIONS =================

// Global State
let currentPage = 1;
let totalPages = 1;
let isLoading = false;
let cachedEvents = {};
let activeFilters = {
    search: '',
    category: '',
    location: '',
    date_start: '',
    date_end: '',
    price_max: '',
    sort_by: 'upcoming'
};

// DOM Elements
let eventsFilterSearch, categoryPills, locationSelect, sortSelect, dateStartInput, dateEndInput, priceRange, priceDisplay, eventsGrid, btnReset, loadMoreTrigger, detailsModal, modalOverlay;

// Debounce helper to avoid hitting the server on every keystroke/slider adjustment
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Initialise Elements
document.addEventListener('DOMContentLoaded', () => {
    // Select elements
    eventsFilterSearch = document.getElementById('search-input');
    categoryPills = document.querySelectorAll('.category-pill');
    locationSelect = document.getElementById('location-select');
    sortSelect = document.getElementById('sort-select');
    dateStartInput = document.getElementById('date-start');
    dateEndInput = document.getElementById('date-end');
    priceRange = document.getElementById('price-range');
    priceDisplay = document.getElementById('price-display');
    eventsGrid = document.getElementById('events-grid');
    btnReset = document.getElementById('btn-reset');
    loadMoreTrigger = document.getElementById('load-more-trigger');
    detailsModal = document.getElementById('details-modal');
    modalOverlay = document.getElementById('modal-overlay');

    // Bind event listeners if elements exist
    if (eventsFilterSearch) eventsFilterSearch.addEventListener('input', debounce(handleSearchChange, 350));
    if (locationSelect) locationSelect.addEventListener('change', handleFilterChange);
    if (sortSelect) sortSelect.addEventListener('change', handleFilterChange);
    if (dateStartInput) dateStartInput.addEventListener('change', handleFilterChange);
    if (dateEndInput) dateEndInput.addEventListener('change', handleFilterChange);
    
    if (priceRange) {
        priceRange.addEventListener('input', (e) => {
            if (priceDisplay) priceDisplay.textContent = `NPR ${parseInt(e.target.value).toLocaleString()}`;
        });
        priceRange.addEventListener('change', debounce(handleFilterChange, 250));
    }

    if (btnReset) btnReset.addEventListener('click', resetAllFilters);

    // Bind category pills
    categoryPills.forEach(pill => {
        pill.addEventListener('click', () => {
            categoryPills.forEach(p => p.classList.remove('active'));
            
            const categoryValue = pill.getAttribute('data-category');
            if (activeFilters.category === categoryValue) {
                // Toggle off
                activeFilters.category = '';
            } else {
                // Toggle on
                pill.classList.add('active');
                activeFilters.category = categoryValue;
            }
            
            currentPage = 1;
            fetchEvents(1, false);
        });
    });

    // Setup Infinite Scroll using Intersection Observer
    setupInfiniteScroll();

    // Setup Close Modal click outside
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
    }

    // Modal forms calculation
    const peopleInput = document.getElementById('booking-people');
    if (peopleInput) {
        peopleInput.addEventListener('input', calculateModalTotal);
    }

    // View Switcher Setup
    const toggleGridBtn = document.getElementById('toggle-grid-view');
    const toggleTimelineBtn = document.getElementById('toggle-timeline-view');
    const toggleContainer = document.querySelector('.view-toggle-container');
    const timelineLayout = document.getElementById('timeline-planner-layout');
    const gridLayout = document.getElementById('main-events-layout');

    if (toggleGridBtn && toggleTimelineBtn) {
        toggleGridBtn.addEventListener('click', () => {
            toggleGridBtn.classList.add('active');
            toggleTimelineBtn.classList.remove('active');
            if (toggleContainer) toggleContainer.classList.remove('timeline-active');
            if (gridLayout) gridLayout.classList.remove('hidden');
            if (timelineLayout) timelineLayout.classList.add('hidden');
        });

        toggleTimelineBtn.addEventListener('click', () => {
            toggleTimelineBtn.classList.add('active');
            toggleGridBtn.classList.remove('active');
            if (toggleContainer) toggleContainer.classList.add('timeline-active');
            if (gridLayout) gridLayout.classList.add('hidden');
            if (timelineLayout) timelineLayout.classList.remove('hidden');
            initTimelinePlanner();
        });
    }
});

// Event Handler for input/select changes
function handleSearchChange(e) {
    activeFilters.search = e.target.value.trim();
    currentPage = 1;
    fetchEvents(1, false);
}

function handleFilterChange() {
    activeFilters.location = locationSelect ? locationSelect.value : '';
    activeFilters.sort_by = sortSelect ? sortSelect.value : 'upcoming';
    activeFilters.date_start = dateStartInput ? dateStartInput.value : '';
    activeFilters.date_end = dateEndInput ? dateEndInput.value : '';
    activeFilters.price_max = priceRange ? priceRange.value : '';
    
    currentPage = 1;
    fetchEvents(1, false);
}

function resetAllFilters() {
    if (eventsFilterSearch) eventsFilterSearch.value = '';
    if (locationSelect) locationSelect.value = '';
    if (sortSelect) sortSelect.value = 'upcoming';
    if (dateStartInput) dateStartInput.value = '';
    if (dateEndInput) dateEndInput.value = '';
    
    categoryPills.forEach(p => p.classList.remove('active'));
    
    if (priceRange) {
        priceRange.value = priceRange.max;
        if (priceDisplay) priceDisplay.textContent = `NPR ${parseInt(priceRange.max).toLocaleString()}`;
    }

    activeFilters = {
        search: '',
        category: '',
        location: '',
        date_start: '',
        date_end: '',
        price_max: '',
        sort_by: 'upcoming'
    };

    currentPage = 1;
    fetchEvents(1, false);
}

// Fetch events from server
async function fetchEvents(page = 1, append = false) {
    if (isLoading) return;
    isLoading = true;

    // Show skeletons on initial load (non-append)
    if (!append) {
        showSkeletons();
    }

    // Build URL query parameters
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('per_page', 6);
    
    for (const [key, value] of Object.entries(activeFilters)) {
        if (value) params.append(key, value);
    }

    try {
        const response = await fetch(`/api/events?${params.toString()}`);
        if (!response.ok) throw new Error('API fetch failed');
        
        const data = await response.json();
        
        currentPage = data.page;
        totalPages = data.total_pages;

        renderEvents(data.events, append);
        
        // Update header count
        const countHeader = document.getElementById('events-count-header');
        if (countHeader) {
            countHeader.textContent = `Showing ${data.total_events} Epic Event${data.total_events !== 1 ? 's' : ''}`;
        }

    } catch (err) {
        console.error('Error fetching events:', err);
        showErrorState();
    } finally {
        isLoading = false;
        
        // Check if we need to hide the loading trigger
        updateLoadMoreState();
    }
}

// Show skeleton cards during loading
function showSkeletons() {
    if (!eventsGrid) return;
    
    let skeletonHtml = '';
    for (let i = 0; i < 3; i++) {
        skeletonHtml += `
            <div class="skeleton-card">
                <div class="skeleton-img skeleton-pulse"></div>
                <div class="skeleton-body">
                    <div class="skeleton-line skeleton-pulse mid"></div>
                    <div class="skeleton-line skeleton-pulse"></div>
                    <div class="skeleton-line skeleton-pulse short"></div>
                    <div class="skeleton-line skeleton-pulse btn"></div>
                </div>
            </div>
        `;
    }
    eventsGrid.innerHTML = skeletonHtml;
}

// Show error state card
function showErrorState() {
    if (!eventsGrid) return;
    eventsGrid.innerHTML = `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <h3 data-i18n="events.error-title">Oops! Something went wrong</h3>
            <p data-i18n="events.error-desc">Failed to retrieve challenges. Please try reloading or check your internet connection.</p>
        </div>
    `;
    if (window.ThrillLang) {
        window.ThrillLang.applyLang(window.ThrillLang.getLang());
    }
}

// Setup intersection observer
function setupInfiniteScroll() {
    if (!loadMoreTrigger) return;
    
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && currentPage < totalPages && !isLoading) {
            fetchEvents(currentPage + 1, true);
        }
    }, {
        rootMargin: '100px',
        threshold: 0.1
    });

    observer.observe(loadMoreTrigger);
}

function updateLoadMoreState() {
    if (!loadMoreTrigger) return;
    if (currentPage >= totalPages || totalPages <= 1) {
        loadMoreTrigger.style.display = 'none';
    } else {
        loadMoreTrigger.style.display = 'flex';
    }
}

// Render event cards into grid
function renderEvents(events, append = false) {
    if (!eventsGrid) return;
    
    // Store in global cache
    events.forEach(evt => {
        cachedEvents[evt.id] = evt;
    });

    if (events.length === 0 && !append) {
        eventsGrid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <h3 data-i18n="events.no-results-title">No Matching Events Found</h3>
                <p data-i18n="events.no-results-desc">Try broadening your search term or adjusting filter values.</p>
            </div>
        `;
        if (window.ThrillLang) {
            window.ThrillLang.applyLang(window.ThrillLang.getLang());
        }
        return;
    }

    let cardsHtml = '';
    events.forEach((evt, idx) => {
        // Date parsing helper
        let formattedDate = 'TBD';
        try {
            const d = new Date(evt.date_time);
            const lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
            const locale = lang === 'ne' ? 'ne-NP' : 'en-US';
            formattedDate = d.toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' }) + ' ' + d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
        } catch (e) {}

        const badgeHtml = evt.badge ? `<div class="badge-overlay ${evt.badge.toLowerCase()}">${evt.badge}</div>` : '';
        const lowTicketWarningHtml = evt.tickets_left <= 5 ? `
            <div class="low-tickets">
                <span class="pulse-warning"></span>
                <span data-i18n="wish.hurry">Hurry! Only</span> ${evt.tickets_left} <span data-i18n="wish.tickets-left">tickets left!</span>
            </div>
        ` : '';

        // Check if in wishlist from user wishlist ids
        let savedClass = '';
        if (window.userWishlistIds && window.userWishlistIds.includes(`event_${evt.id}`)) {
            savedClass = 'is-saved';
        }

        cardsHtml += `
            <div class="event-card" style="animation-delay: ${idx * 0.05}s">
                <div class="img-wrap">
                    <img src="/static/images/${evt.image_url}" alt="${evt.title}" onerror="this.src='/static/images/Mountain-Main.png';">
                    ${badgeHtml}
                    <button class="wishlist-btn ${savedClass}" 
                            data-activity-id="event_${evt.id}" 
                            onclick="toggleEventWishlist(event, 'event_${evt.id}')"
                            aria-label="Add to Wishlist">
                        <svg class="heart-icon" viewBox="0 0 24 24">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                        </svg>
                    </button>
                    <div class="location-badge">
                        <svg viewBox="0 0 24 24" width="12" height="12"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z" fill="currentColor"/></svg>
                        ${evt.location}
                    </div>
                </div>
                <div class="card-content">
                    <span class="category-label">${evt.category}</span>
                    <h3>${evt.title}</h3>
                    <p class="desc">${evt.description || 'No description provided.'}</p>
                    
                    <div class="meta-grid">
                        <div class="meta-item">
                            <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                            ${formattedDate}
                        </div>
                        <div class="meta-item">
                            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                            ${evt.duration || '3 hours'}
                        </div>
                        ${lowTicketWarningHtml}
                    </div>
                    
                    <div class="card-footer">
                        <div class="price-section">
                            <span class="price-label" data-i18n="wish.price-per">Price per person</span>
                            <span class="price-value">NPR ${parseInt(evt.price).toLocaleString()}</span>
                        </div>
                        <a href="/events/${evt.id}" class="btn-details" data-i18n="events.view-details">View Details</a>
                    </div>
                </div>
            </div>
        `;
    });

    if (append) {
        eventsGrid.insertAdjacentHTML('beforeend', cardsHtml);
    } else {
        eventsGrid.innerHTML = cardsHtml;
    }

    if (window.ThrillLang) {
        window.ThrillLang.applyLang(window.ThrillLang.getLang());
    }
}

// Wishlist toggle integration
async function toggleEventWishlist(event, activityId) {
    event.preventDefault();
    event.stopPropagation();

    // Check user authenticated
    const wishlistLink = document.querySelector('.nav-wishlist-link');
    if (!wishlistLink) {
        // Not logged in (no wishlist link visible)
        window.location.href = `/login?next=${encodeURIComponent(window.location.href)}`;
        return;
    }

    const btn = event.currentTarget || event.target.closest('.wishlist-btn') || event.target;
    btn.disabled = true;

    try {
        const response = await fetch('/wishlist/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ activity_id: activityId })
        });

        if (response.status === 401) {
            window.location.href = `/login?next=${encodeURIComponent(window.location.href)}`;
            return;
        }
        if (!response.ok) throw new Error('Wishlist toggle request failed');
        const data = await response.json();

        if (data.status === 'success') {
            if (data.saved) {
                btn.classList.add('is-saved');
                if (window.userWishlistIds && !window.userWishlistIds.includes(activityId)) {
                    window.userWishlistIds.push(activityId);
                }
            } else {
                btn.classList.remove('is-saved');
                if (window.userWishlistIds) {
                    window.userWishlistIds = window.userWishlistIds.filter(id => id !== activityId);
                }
            }

            // Sync other buttons for the same event on page if they exist
            const matches = document.querySelectorAll(`.wishlist-btn[data-activity-id="${activityId}"]`);
            matches.forEach(match => {
                if (data.saved) {
                    match.classList.add('is-saved');
                } else {
                    match.classList.remove('is-saved');
                }
            });

            // Update badge count
            const badge = document.querySelector('.wishlist-badge');
            if (badge) {
                let count = parseInt(badge.textContent) || 0;
                let newCount = data.saved ? count + 1 : count - 1;
                if (newCount <= 0) {
                    badge.remove();
                } else {
                    badge.textContent = newCount;
                }
            } else if (data.saved) {
                const navLink = document.querySelector('.nav-wishlist-link');
                if (navLink) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'wishlist-badge';
                    newBadge.textContent = '1';
                    navLink.appendChild(newBadge);
                }
            }
        }
    } catch (err) {
        console.error('Wishlist toggle error:', err);
    } finally {
        btn.disabled = false;
    }
}

// Details Modal handlers
let selectedEvent = null;

async function openDetailsModal(eventId) {
    if (!detailsModal || !modalOverlay) return;

    try {
        let event = cachedEvents[eventId];
        if (!event) {
            // Re-fetch elements if not found in current page cache (e.g. from direct link or fallback)
            const fallback = await fetch(`/api/events?page=1&per_page=100`);
            if (!fallback.ok) throw new Error('Failed to fetch events');
            const fallbackData = await fallback.json();
            (fallbackData.events || []).forEach(e => {
                cachedEvents[e.id] = e;
            });
            event = cachedEvents[eventId];
        }

        if (!event) {
            console.error('Event not found:', eventId);
            return;
        }

        selectedEvent = event;

        // Populate Modal contents
        document.getElementById('modal-img').src = `/static/images/${selectedEvent.image_url}`;
        document.getElementById('modal-title').textContent = selectedEvent.title;
        document.getElementById('modal-desc').textContent = selectedEvent.description || 'Come and experience the thrill!';
        document.getElementById('modal-category').textContent = selectedEvent.category;
        document.getElementById('modal-location').textContent = selectedEvent.location;
        document.getElementById('modal-duration').textContent = selectedEvent.duration || '3 hours';
        document.getElementById('modal-tickets-left').textContent = `${selectedEvent.tickets_left} / 50 seats left`;

        let formattedDate = 'TBD';
        try {
            const d = new Date(selectedEvent.date_time);
            formattedDate = d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' }) + ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        } catch (e) {}
        document.getElementById('modal-date').textContent = formattedDate;

        // Update Tickets Progress Bar
        const progressFill = document.getElementById('modal-progress-fill');
        if (progressFill) {
            const percentage = (selectedEvent.tickets_left / 50) * 100;
            progressFill.style.width = `${percentage}%`;
            if (selectedEvent.tickets_left <= 5) {
                progressFill.classList.add('low');
            } else {
                progressFill.classList.remove('low');
            }
        }

        // Setup Booking Date value
        const dateInput = document.getElementById('booking-date');
        if (dateInput) {
            // Set date value to match event date (YYYY-MM-DD format)
            const dateStr = getEventDateStr(selectedEvent);
            dateInput.value = dateStr;
            dateInput.min = dateStr; // Cannot book past or before this exact day
            dateInput.max = dateStr;
        }

        // Reset people count to 1 and calculate total
        const peopleInput = document.getElementById('booking-people');
        if (peopleInput) {
            peopleInput.value = 1;
            peopleInput.max = selectedEvent.tickets_left;
        }
        calculateModalTotal();

        // Update booking button state
        const btnBook = document.getElementById('btn-book-submit');
        if (btnBook) {
            if (selectedEvent.tickets_left <= 0) {
                btnBook.disabled = true;
                btnBook.textContent = 'Sold Out';
            } else {
                btnBook.disabled = false;
                btnBook.textContent = 'Confirm Booking';
            }
        }

        // Open Modal overlay
        modalOverlay.classList.add('is-active');
        document.body.style.overflow = 'hidden'; // Lock scroll

    } catch (err) {
        console.error('Error opening details modal:', err);
    }
}

function closeModal() {
    if (!modalOverlay) return;
    modalOverlay.classList.remove('is-active');
    document.body.style.overflow = ''; // Unlock scroll
    selectedEvent = null;
}

function calculateModalTotal() {
    if (!selectedEvent) return;
    
    const peopleInput = document.getElementById('booking-people');
    const totalSpan = document.getElementById('modal-total-price');
    if (!peopleInput || !totalSpan) return;

    let peopleCount = parseInt(peopleInput.value) || 1;
    
    // Boundary check
    if (peopleCount < 1) {
        peopleCount = 1;
        peopleInput.value = 1;
    } else if (peopleCount > selectedEvent.tickets_left) {
        peopleCount = selectedEvent.tickets_left;
        peopleInput.value = selectedEvent.tickets_left;
    }

    const totalCost = selectedEvent.price * peopleCount;
    totalSpan.textContent = `NPR ${totalCost.toLocaleString()}`;
}

// Handle Modal Booking Submission
async function submitBooking(event) {
    event.preventDefault();
    if (!selectedEvent) return;

    const peopleInput = document.getElementById('booking-people');
    const dateInput = document.getElementById('booking-date');
    const btnBook = document.getElementById('btn-book-submit');
    if (!peopleInput || !dateInput || !btnBook) return;

    btnBook.disabled = true;
    btnBook.textContent = 'Processing...';

    try {
        const response = await fetch('/api/events/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_id: selectedEvent.id,
                date: dateInput.value,
                people: parseInt(peopleInput.value) || 1
            })
        });

        const data = await response.json();
        
        if (response.status === 401) {
            // Redirect to login
            closeModal();
            window.location.href = `/login?next=${encodeURIComponent(window.location.href)}`;
            return;
        }

        if (response.ok && data.status === 'success') {
            // Show successful message and redirect
            showToastMessage('success', data.message);
            closeModal();
            
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 1000);
        } else {
            showToastMessage('error', data.message || 'Booking failed.');
            btnBook.disabled = false;
            btnBook.textContent = 'Confirm Booking';
        }

    } catch (err) {
        console.error('Booking submission error:', err);
        showToastMessage('error', 'Connection error. Please try again.');
        btnBook.disabled = false;
        btnBook.textContent = 'Confirm Booking';
    }
}

// Toast helper in case global toast container exists
function showToastMessage(category, message) {
    const container = document.getElementById('global-toast-container') || document.body;
    
    // Create toast div
    const toast = document.createElement('div');
    toast.className = `toast-msg-item ${category}`;
    
    // SVG icons
    let iconSvg = '';
    if (category === 'success') {
        iconSvg = `<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>`;
    } else {
        iconSvg = `<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`;
    }
    
    toast.innerHTML = `
        <div class="toast-icon">${iconSvg}</div>
        <div class="toast-text">${message}</div>
        <button class="toast-close-btn">&times;</button>
    `;
    
    // Add close listener
    toast.onclick = () => toast.remove();
    
    if (container === document.body) {
        // Style floating container if no container exists
        toast.style.position = 'fixed';
        toast.style.top = '24px';
        toast.style.right = '24px';
        toast.style.zIndex = '9999';
    }
    
    container.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        toast.style.transition = 'transform 0.4s ease, opacity 0.4s ease, filter 0.4s ease';
        toast.style.transform = 'translateY(-20px) scale(0.9)';
        toast.style.opacity = '0';
        toast.style.filter = 'blur(4px)';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ================= WEEKLY TIMELINE PLANNER LOGIC =================
let allEventsList = [];
let hasTimelineLoaded = false;

function getEventDateStr(evt) {
    if (!evt || !evt.date_time) return '';
    const raw = String(evt.date_time);
    if (raw.length >= 10 && raw.charAt(4) === '-' && raw.charAt(7) === '-') {
        return raw.substring(0, 10);
    }
    try {
        const d = new Date(raw);
        if (!isNaN(d.getTime())) {
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${y}-${m}-${day}`;
        }
    } catch (e) {}
    return raw.substring(0, 10);
}

async function initTimelinePlanner() {
    if (hasTimelineLoaded) return;

    const weekStrip = document.getElementById('week-strip');
    if (weekStrip) {
        weekStrip.innerHTML = '<div class="skeleton-pulse" style="grid-column: 1/-1; height: 60px; border-radius: 12px; opacity: 0.3;"></div>';
    }

    try {
        const response = await fetch('/api/events?page=1&per_page=100');
        if (!response.ok) throw new Error(`API error: ${response.status}`);

        const data = await response.json();
        allEventsList = data.events || [];
        allEventsList.forEach(evt => {
            cachedEvents[evt.id] = evt;
        });
        hasTimelineLoaded = true;

        buildWeekStripCalendar();
        renderTimeline();
    } catch (err) {
        console.error('Timeline initialization error:', err);
        // Reset flag so clicking the button again retries the fetch
        hasTimelineLoaded = false;
        if (weekStrip) weekStrip.innerHTML = '';
        const container = document.getElementById('timeline-container');
        if (container) {
            container.innerHTML = '<div class="timeline-empty-card"><h4>Failed to Load Schedule</h4><p>There was an error pulling the upcoming events.</p><button class="btn-suggest-all" onclick="initTimelinePlanner()">Retry</button></div>';
        }
    }
}

function toNepaliDigits(num) {
    const nepaliDigits = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'];
    return String(num).split('').map(digit => {
        return nepaliDigits[parseInt(digit)] || digit;
    }).join('');
}

function buildWeekStripCalendar() {
    const weekStrip = document.getElementById('week-strip');
    if (!weekStrip) return;

    const days = [];
    const today = new Date();
    const lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
    
    const weekdayNamesEn = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekdayNamesNe = ['आइत', 'सोम', 'मंगल', 'बुध', 'बिही', 'शुक्र', 'शनि'];
    const weekdayNames = lang === 'ne' ? weekdayNamesNe : weekdayNamesEn;
    
    for (let i = 0; i < 7; i++) {
        const current = new Date(today);
        current.setDate(today.getDate() + i);
        
        const year = current.getFullYear();
        const month = String(current.getMonth() + 1).padStart(2, '0');
        const day = String(current.getDate()).padStart(2, '0');
        
        days.push({
            dateObj: current,
            dayName: i === 0 ? (lang === 'ne' ? 'आज' : 'Today') : weekdayNames[current.getDay()],
            dayNum: lang === 'ne' ? toNepaliDigits(current.getDate()) : current.getDate(),
            isoDate: `${year}-${month}-${day}`
        });
    }

    let pillsHtml = '';
    days.forEach(day => {
        const hasEvent = allEventsList.some(evt => getEventDateStr(evt) === day.isoDate);
        const dotHtml = hasEvent ? '<span class="has-event-dot"></span>' : '';
        const todayClass = (day.dayName === 'Today' || day.dayName === 'आज') ? 'is-today' : '';

        pillsHtml += `
            <div class="day-pill ${todayClass}" data-date="${day.isoDate}" onclick="handleDayPillClick(event)">
                <span class="day-name">${day.dayName}</span>
                <span class="day-number">${day.dayNum}</span>
                ${dotHtml}
            </div>
        `;
    });

    weekStrip.innerHTML = pillsHtml;
}

function handleDayPillClick(event) {
    const pill = event.currentTarget;
    const dateStr = pill.getAttribute('data-date');
    const isActive = pill.classList.contains('active');

    document.querySelectorAll('.day-pill').forEach(p => p.classList.remove('active'));

    if (isActive) {
        renderTimeline(null);
    } else {
        pill.classList.add('active');
        renderTimeline(dateStr);
    }
}

window.resetTimelinePills = function() {
    document.querySelectorAll('.day-pill').forEach(p => p.classList.remove('active'));
    renderTimeline(null);
};

function createTimelineCardHtml(evt) {
    let formattedDate = 'TBD';
    let formattedTime = 'All Day';
    let isToday = false;
    try {
        const d = new Date(evt.date_time);
        const lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
        const locale = lang === 'ne' ? 'ne-NP' : 'en-US';
        formattedDate = d.toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' });
        formattedTime = d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
        
        const today = new Date();
        if (d.toDateString() === today.toDateString()) {
            isToday = true;
        }
    } catch (e) {}

    const badgeHtml = isToday ? `
        <div class="live-pulse-badge">
            <span class="live-dot"></span>
            <span data-i18n="events.live-today">Live Today</span>
        </div>
    ` : (evt.badge ? `<span class="category-tag">${evt.badge}</span>` : '');

    const timeClass = isToday ? 'event-time today-time' : 'event-time';
    const cardClass = isToday ? 'timeline-card today-highlight' : 'timeline-card';
    
    const ticketsPct = Math.min(100, Math.max(0, (evt.tickets_left / 50) * 100));
    const isWarning = evt.tickets_left <= 5 ? 'warning' : '';

    return `
        <div class="${cardClass}" onclick="window.location.href='/events/${evt.id}'">
            <div class="card-thumb">
                <img src="/static/images/${evt.image_url}" alt="${evt.title}" onerror="this.src='/static/images/Mountain-Main.png';">
            </div>
            <div class="card-info">
                <div class="info-header">
                    <span class="${timeClass}">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        ${formattedTime}
                    </span>
                    ${badgeHtml}
                </div>
                <h4>${evt.title}</h4>
                <p class="desc">${evt.description || 'No description provided.'}</p>
                <div class="meta-row">
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                        <span>${formattedDate}</span>
                    </div>
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z" fill="currentColor"/></svg>
                        <span>${evt.location}</span>
                    </div>
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>${evt.duration || '3 hours'}</span>
                    </div>
                </div>
            </div>
            <div class="card-action" onclick="event.stopPropagation();">
                <div class="price-tag">
                    <span data-i18n="events.tickets-from">Tickets from</span>
                    <span>NPR ${parseInt(evt.price).toLocaleString()}</span>
                </div>
                <a href="/events/${evt.id}" class="btn-book-timeline" data-i18n="events.book-spot">Book Spot</a>
                <div class="timeline-seats-bar">
                    <div class="seats-label">${evt.tickets_left} <span data-i18n="event-detail.seats-left-label">seats left</span></div>
                    <div class="seats-progress-bg">
                        <div class="seats-progress-fill ${isWarning}" style="width: ${ticketsPct}%"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderTimeline(filteredDate = null) {
    const container = document.getElementById('timeline-container');
    if (!container) return;

    if (!allEventsList || allEventsList.length === 0) {
        container.innerHTML = `
            <div class="timeline-empty-card">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <h4 data-i18n="events.timeline-empty-title">No Events Scheduled</h4>
                <p data-i18n="events.timeline-empty-desc">There are no upcoming adventure events in our database at this moment.</p>
            </div>
        `;
        if (window.ThrillLang) {
            window.ThrillLang.applyLang(window.ThrillLang.getLang());
        }
        return;
    }

    let events = [...allEventsList];
    if (filteredDate) {
        events = events.filter(evt => getEventDateStr(evt) === filteredDate);
    }

    if (events.length === 0) {
        let dayDisplay = filteredDate;
        try {
            const d = new Date(filteredDate);
            const lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
            dayDisplay = d.toLocaleDateString(lang === 'ne' ? 'ne-NP' : 'en-US', { weekday: 'long', month: 'short', day: 'numeric' });
        } catch(e) {}
        
        container.innerHTML = `
            <div class="timeline-empty-card" style="animation: fadeIn 0.3s ease-out;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <h4 data-i18n="events.timeline-no-adventures-title">No Adventures Scheduled</h4>
                <p data-i18n="events.timeline-no-adventures-desc">There are no organized trips scheduled for this date. Check out other dates or click below to view the full upcoming weekly schedule.</p>
                <button class="btn-suggest-all" onclick="resetTimelinePills()" data-i18n="events.timeline-view-all">View All Days</button>
            </div>
        `;
        if (window.ThrillLang) {
            window.ThrillLang.applyLang(window.ThrillLang.getLang());
        }
        return;
    }

    events.sort((a, b) => new Date(a.date_time) - new Date(b.date_time));

    const groups = {};
    events.forEach(evt => {
        const dateStr = getEventDateStr(evt);
        if (!groups[dateStr]) {
            groups[dateStr] = [];
        }
        groups[dateStr].push(evt);
    });

    let timelineHtml = '';
    const now = new Date();
    const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
    const locale = lang === 'ne' ? 'ne-NP' : 'en-US';

    Object.keys(groups).forEach(dateStr => {
        const groupEvents = groups[dateStr];
        let groupTitle = '';
        let dateLabel = '';
        let nodeClass = 'timeline-node';
        let groupClass = 'timeline-day-group';

        try {
            const d = new Date(dateStr + 'T00:00:00');
            if (dateStr === todayStr) {
                groupTitle = lang === 'ne' ? 'आज' : 'Today';
                dateLabel = d.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
                nodeClass += ' today-node';
                groupClass += ' active-group';
            } else {
                groupTitle = d.toLocaleDateString(locale, { weekday: 'long' });
                dateLabel = d.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
            }
        } catch (e) {
            groupTitle = dateStr;
        }

        let cardsHtml = '';
        groupEvents.forEach(evt => {
            cardsHtml += createTimelineCardHtml(evt);
        });

        const dayAbbrev = groupTitle.substring(0, 3).toUpperCase();

        timelineHtml += `
            <div class="${groupClass}" data-group-date="${dateStr}">
                <div class="${nodeClass}">${dayAbbrev}</div>
                <h3 class="timeline-group-title">
                    ${groupTitle} <span class="date-label">(${dateLabel})</span>
                </h3>
                <div class="timeline-items-list">
                    ${cardsHtml}
                </div>
            </div>
        `;
    });

    container.innerHTML = timelineHtml;

    if (window.ThrillLang) {
        window.ThrillLang.applyLang(window.ThrillLang.getLang());
    }
}

// Expose handlers for inline onclick attributes in server-rendered markup
window.toggleEventWishlist = toggleEventWishlist;
window.initTimelinePlanner = initTimelinePlanner;
window.handleDayPillClick = handleDayPillClick;

// Listen for language changes to update weekly strip and grid contents
window.addEventListener('languagechange', () => {
    if (hasTimelineLoaded) {
        buildWeekStripCalendar();
        renderTimeline();
    }
    // Re-fetch or refresh current active page events
    currentPage = 1;
    fetchEvents(1, false);
});