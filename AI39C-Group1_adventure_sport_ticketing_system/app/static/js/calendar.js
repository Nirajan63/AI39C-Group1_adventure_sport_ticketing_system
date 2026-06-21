// calendar.js — Thrill Sphere — My Calendar
// Single source of truth:
//   window.THRILL_BOOKINGS     — user's own bookings (from Flask/Jinja2)
//   window.THRILL_AVAILABILITY — live fill-rate per activity per date (all users)

(function () {
    'use strict';

    // ── Helpers ───────────────────────────────────────────────────────
    function todayDateStr() {
        var d = new Date();
        var m = ('0' + (d.getMonth() + 1)).slice(-2);
        var day = ('0' + d.getDate()).slice(-2);
        return d.getFullYear() + '-' + m + '-' + day;
    }

    // ── Build event map from real booking data ─────────────────────────
    // Merges THRILL_BOOKINGS with THRILL_AVAILABILITY to compute the
    // correct dot colour for every booked date.
    function buildEventMapFromBookings() {
        var bookings = (typeof window.THRILL_BOOKINGS     !== 'undefined') ? window.THRILL_BOOKINGS     : [];
        var avail    = (typeof window.THRILL_AVAILABILITY !== 'undefined') ? window.THRILL_AVAILABILITY : {};
        var nowStr   = todayDateStr();
        var eventMap = {};

        bookings.forEach(function (b) {
            if (b.status === 'cancelled') return;

            var dateStr = b.date; // 'YYYY-MM-DD'
            if (!dateStr) return;

            var parts = dateStr.split('-');
            if (parts.length !== 3) return;

            var y = parseInt(parts[0], 10);
            var m = parseInt(parts[1], 10) - 1; // JS months 0-based
            var d = parseInt(parts[2], 10);
            if (isNaN(y) || isNaN(m) || isNaN(d)) return;

            var key = y + '-' + m + '-' + d;
            if (!eventMap[key]) eventMap[key] = [];

            // ── Dot colour logic ─────────────────────────────────────
            // Past / completed → amber ('limited')
            // Future → driven by live availability status
            var isPast    = dateStr < nowStr;
            var dateAvail = avail[dateStr] || {};
            var actAvail  = dateAvail[b.activity] || {};

            var calStatus;
            if (isPast || b.status === 'completed') {
                calStatus = 'limited';  // amber — adventure done
            } else {
                // Use live availability; default to 'available' if no data yet
                calStatus = actAvail.status || 'available';
            }

            eventMap[key].push({
                name:          b.activity || 'Adventure',
                location:      b.location || 'Nepal',
                duration:      b.duration || '—',
                price:         parseFloat(b.total)      || 0,
                people:        parseInt(b.people, 10)   || 1,
                status:        calStatus,           // controls dot colour
                bookingStatus: b.status,            // confirmed | completed
                // Availability details for the event panel
                availStatus:   actAvail.status      || 'available',
                remaining:     (actAvail.remaining  !== undefined) ? actAvail.remaining : null,
                capacity:      actAvail.capacity    || null,
                fillPct:       actAvail.fill_pct    || 0,
            });
        });

        return eventMap;
    }

    // ── State ─────────────────────────────────────────────────────────
    var today       = new Date();
    var curYear     = today.getFullYear();
    var curMonth    = today.getMonth();
    var selectedDay = null;
    var eventMap    = buildEventMapFromBookings();

    // ── DOM refs ──────────────────────────────────────────────────────
    var calGrid, calMonthLabel, calPrev, calNext,
        calEventsDate, calEventsList;

    // ── Init ──────────────────────────────────────────────────────────
    function init() {
        calGrid       = document.getElementById('calGrid');
        calMonthLabel = document.getElementById('calMonthLabel');
        calPrev       = document.getElementById('calPrev');
        calNext       = document.getElementById('calNext');
        calEventsDate = document.getElementById('calEventsDate');
        calEventsList = document.getElementById('calEventsList');

        if (!calGrid) return;

        calPrev.addEventListener('click', function () {
            curMonth--;
            if (curMonth < 0) { curMonth = 11; curYear--; }
            render();
        });

        calNext.addEventListener('click', function () {
            curMonth++;
            if (curMonth > 11) { curMonth = 0; curYear++; }
            render();
        });

        render();
    }

    // Helper to get translated month names
    function getMonthName(m) {
        var enMonths = ['January','February','March','April','May','June',
                        'July','August','September','October','November','December'];
        if (window.ThrillLang && window.ThrillLang.getLang) {
            var lang = window.ThrillLang.getLang();
            if (lang === 'ne') {
                var neMonths = ['जनवरी','फेब्रुअरी','मार्च','अप्रिल','मे','जुन',
                                'जुलाई','अगस्त','सेप्टेम्बर','अक्टोबर','नोभेम्बर','डिसेम्बर'];
                return neMonths[m];
            }
        }
        return enMonths[m];
    }

    // Helper to translate english digits to nepali digits
    function translateDigits(str, lang) {
        if (str === null || str === undefined) return '';
        if (lang === 'ne') {
            return str.toString().replace(/\d/g, function (d) {
                return '०१२३४५६७८९'[d];
            });
        }
        return str.toString();
    }

    // ── Render calendar ───────────────────────────────────────────────
    function render() {
        var lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';
        calMonthLabel.textContent = getMonthName(curMonth) + ' ' + translateDigits(curYear, lang);
        calGrid.innerHTML = '';

        var firstDay    = new Date(curYear, curMonth, 1).getDay();
        var daysInMonth = new Date(curYear, curMonth + 1, 0).getDate();
        var todayNorm   = new Date(today.getFullYear(), today.getMonth(), today.getDate());

        // Empty leading cells
        for (var i = 0; i < firstDay; i++) {
            var empty = document.createElement('div');
            empty.className = 'cal-day cal-empty';
            calGrid.appendChild(empty);
        }

        // Day cells
        for (var d = 1; d <= daysInMonth; d++) {
            var cell    = document.createElement('div');
            cell.className = 'cal-day';

            var dateObj = new Date(curYear, curMonth, d);
            var key     = curYear + '-' + curMonth + '-' + d;
            var events  = eventMap[key] || [];

            var isToday = (d === today.getDate() &&
                           curMonth === today.getMonth() &&
                           curYear  === today.getFullYear());
            var isPast  = dateObj < todayNorm;

            if (isToday) cell.classList.add('cal-today');
            if (isPast)  cell.classList.add('cal-past');

            // Restore pointer-events on past dates that DO have bookings
            // (so user can still click to see completed adventure info)
            if (isPast && events.length > 0) {
                cell.style.pointerEvents = 'auto';
                cell.style.color = '';  // restore readable colour
            }

            if (selectedDay &&
                selectedDay.d === d &&
                selectedDay.m === curMonth &&
                selectedDay.y === curYear) {
                cell.classList.add('cal-selected');
            }

            var numEl = document.createElement('span');
            numEl.className = 'cal-day-num';
            numEl.textContent = translateDigits(d, lang);
            cell.appendChild(numEl);

            if (events.length > 0) {
                var dominant = getDominantStatus(events);
                cell.classList.add('cal-has-event', 'cal-' + dominant);

                // Sold-out: add strikethrough on the number, keep clickable
                // so users see "Fully Booked" message (pointer-events kept on)
                if (dominant === 'soldout') {
                    cell.classList.remove('cal-soldout'); // remove css pointer-events:none
                    cell.style.background   = 'rgba(255,79,79,0.06)';
                    cell.style.cursor       = 'pointer';
                    cell.style.pointerEvents = 'auto';
                    numEl.style.textDecoration = 'line-through';
                    numEl.style.opacity        = '0.55';
                }

                var dot = document.createElement('span');
                dot.className = 'cal-event-dot';
                cell.appendChild(dot);

                (function (dayD, evs) {
                    cell.addEventListener('click', function () {
                        document.querySelectorAll('.cal-day.cal-selected').forEach(function (el) {
                            el.classList.remove('cal-selected');
                        });
                        cell.classList.add('cal-selected');
                        selectedDay = { d: dayD, m: curMonth, y: curYear };
                        showEvents(dayD, evs);
                    });
                })(d, events);
            }

            calGrid.appendChild(cell);
        }
    }

    // ── Dominant status for date dot colour ───────────────────────────
    // Priority: soldout > limited > available
    function getDominantStatus(events) {
        if (events.some(function (e) { return e.status === 'soldout'; }))  return 'soldout';
        if (events.some(function (e) { return e.status === 'limited'; }))  return 'limited';
        return 'available';
    }

    // ── Show bookings for the selected date ───────────────────────────
    function showEvents(day, events) {
        var lang = (window.ThrillLang && window.ThrillLang.getLang) ? window.ThrillLang.getLang() : 'en';

        if (lang === 'ne') {
            calEventsDate.textContent = getMonthName(curMonth) + ' ' + translateDigits(day, 'ne') + ', ' + translateDigits(curYear, 'ne');
        } else {
            calEventsDate.textContent = getMonthName(curMonth) + ' ' + day + ', ' + curYear;
        }
        calEventsList.innerHTML   = '';

        if (!events || events.length === 0) {
            var msg = lang === 'ne' ? 'यस मितिमा कुनै बुकिङ छैन।' : 'No bookings on this date.';
            calEventsList.innerHTML =
                '<div class="cal-no-selection"><p>' + msg + '</p></div>';
            return;
        }

        events.forEach(function (ev) {
            var isSoldOut   = ev.availStatus === 'soldout';
            var isLimited   = ev.availStatus === 'limited';
            var isCompleted = ev.bookingStatus === 'completed';
            var isPast      = ev.status === 'limited' && isCompleted;

            // Card class follows dot colour
            var cardClass = 'cal-event-card ev-' + ev.status;
            var card = document.createElement('div');
            card.className = cardClass;

            // ── Booking status label ──────────────────────────────────
            var bookingLabel;
            if (isCompleted) {
                bookingLabel = lang === 'ne' ? '✓ पूरा भएको' : '✓ Completed';
            } else if (isSoldOut) {
                bookingLabel = lang === 'ne' ? '✗ सबै बुकिङ भएको' : '✗ Fully Booked';
            } else if (isLimited) {
                bookingLabel = lang === 'ne' ? '⚡ सीमित सिट' : '⚡ Limited';
            } else {
                bookingLabel = lang === 'ne' ? '📅 पुष्टि भएको — आगामी' : '📅 Confirmed — Upcoming';
            }

            // ── Price / group display ─────────────────────────────────
            var pDisplay = lang === 'ne' ? translateDigits(ev.price.toLocaleString(), 'ne') : ev.price.toLocaleString();
            var priceDisplay = 'NPR ' + pDisplay;
            if (ev.people > 1) {
                var paxLabel = lang === 'ne' ? ' जना' : ' pax';
                priceDisplay += ' · ' + translateDigits(ev.people, lang) + paxLabel;
            } else {
                var paxLabel = lang === 'ne' ? '१ जना' : '1 pax';
                priceDisplay += ' · ' + paxLabel;
            }

            // ── Availability badge (future dates only) ────────────────
            var availBadge = '';
            if (!isCompleted && ev.remaining !== null) {
                var remStr = translateDigits(ev.remaining, lang);
                if (isSoldOut) {
                    var msg = lang === 'ne' ? 'सबै बुकिङ भएको — कुनै स्लट उपलब्ध छैन' : 'Fully Booked — No Slots Available';
                    availBadge =
                        '<div class="cal-avail-badge soldout">' +
                            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" ' +
                                 'width="12" height="12" style="flex-shrink:0">' +
                                '<circle cx="12" cy="12" r="10"/>' +
                                '<line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>' +
                            '</svg>' +
                            msg +
                        '</div>';
                } else if (isLimited) {
                    var msg = lang === 'ne' ? 'सीमित — केवल ' + remStr + ' सिट बाँकी' : 'Limited — Only ' + remStr + ' spot' + (ev.remaining === 1 ? '' : 's') + ' left';
                    availBadge =
                        '<div class="cal-avail-badge limited">' +
                            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" ' +
                                 'width="12" height="12" style="flex-shrink:0">' +
                                '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>' +
                            '</svg>' +
                            msg +
                        '</div>';
                } else {
                    var msg = lang === 'ne' ? remStr + ' सिट उपलब्ध' : remStr + ' spot' + (ev.remaining === 1 ? '' : 's') + ' available';
                    availBadge =
                        '<div class="cal-avail-badge available">' +
                            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" ' +
                                 'width="12" height="12" style="flex-shrink:0">' +
                                '<polyline points="20 6 9 17 4 12"/>' +
                            '</svg>' +
                            msg +
                        '</div>';
                }
            }

            // ── Action button ─────────────────────────────────────────
            var actionBtn = '';
            if (isCompleted) {
                actionBtn = '';
            } else if (isSoldOut) {
                var btnTxt = lang === 'ne' ? '✗ कुनै स्लट उपलब्ध छैन' : '✗ No Slots Available';
                actionBtn =
                    '<button class="cal-ev-book-btn cal-ev-book-btn--soldout" disabled>' +
                        btnTxt +
                    '</button>';
            } else {
                var btnTxt = lang === 'ne' ? 'मेरा बुकिङहरू हेर्नुस् →' : 'View My Bookings →';
                actionBtn =
                    '<button class="cal-ev-book-btn" ' +
                        'onclick="switchSection(\'bookings\', null)">' +
                        btnTxt +
                    '</button>';
            }

            card.innerHTML =
                '<div class="cal-ev-row">' +
                    '<div class="cal-ev-name">' + ev.name + '</div>' +
                    '<div class="cal-ev-price">' + priceDisplay + '</div>' +
                '</div>' +
                '<div class="cal-ev-meta">' +
                    '<span class="cal-ev-pill">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                             '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>' +
                             '<circle cx="12" cy="10" r="3"/>' +
                        '</svg>' +
                        ev.location +
                    '</span>' +
                    '<span class="cal-ev-pill">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                            '<circle cx="12" cy="12" r="10"/>' +
                            '<polyline points="12 6 12 12 16 14"/>' +
                        '</svg>' +
                        ev.duration +
                    '</span>' +
                    (ev.fillPct > 0 ?
                        '<span class="cal-ev-pill">⬆ ' + (lang === 'ne' ? translateDigits(ev.fillPct, 'ne') + '% बुकिङ भएको' : ev.fillPct + '% booked') + '</span>'
                    : '') +
                '</div>' +
                '<div class="cal-ev-status">' + bookingLabel + '</div>' +
                availBadge +
                actionBtn;

            calEventsList.appendChild(card);
        });
    }

    // ── Boot ──────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ── Language Toggle Event Listener ────────────────────────────────
    window.addEventListener('languagechange', function () {
        if (typeof render === 'function') {
            render();
        }
        if (selectedDay && typeof showEvents === 'function') {
            var key = selectedDay.y + '-' + selectedDay.m + '-' + selectedDay.d;
            var events = eventMap[key] || [];
            showEvents(selectedDay.d, events);
        }
    });

})();
