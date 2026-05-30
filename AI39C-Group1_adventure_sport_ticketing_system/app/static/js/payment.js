// payment.js — Thrill Sphere Payment Modal
// Modular, state-driven. Ready for real backend integration.

(function () {
    'use strict';

    // ── State ────────────────────────────────────────────────────────
    const state = {
        isOpen:        false,
        method:        'esewa',   // 'esewa' | 'khalti'
        txnCode:       '',
        status:        null,      // null | 'pending' | 'confirmed' | 'failed'
        booking: {
            activity: '',
            date:     '',
            people:   1,
            total:    0,
        }
    };

    // ── DOM refs (resolved on init) ───────────────────────────────────
    let overlay, modal, closeBtn,
        esewaBtn, khaltiBtn,
        qrImg, qrWrapper,
        qrInstructionText, qrStepText,
        txnInput, submitBtn,
        statusArea,
        bookingActivity, bookingMeta, bookingAmount,
        stepDots, stepLines,
        doneBtn;

    // ── Init ─────────────────────────────────────────────────────────
    function init() {
        injectHTML();
        cacheRefs();
        bindEvents();
        interceptBookForm();
    }

    // ── Inject modal HTML ─────────────────────────────────────────────
    function injectHTML() {
        const html = `
<div class="pm-overlay" id="pmOverlay" role="dialog" aria-modal="true" aria-label="Payment">

  <div class="pm-modal" id="pmModal">

    <!-- Header -->
    <div class="pm-header">
      <div class="pm-header-left">
        <div class="pm-pretitle">Secure Payment</div>
        <div class="pm-title">Complete Booking</div>
        <div class="pm-subtitle">Pay via QR to confirm your adventure</div>
      </div>
      <button class="pm-close" id="pmClose" aria-label="Close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <!-- Booking summary -->
    <div class="pm-booking-strip">
      <div class="pm-booking-info">
        <div class="pm-booking-activity" id="pmActivity">—</div>
        <div class="pm-booking-meta"    id="pmMeta">—</div>
      </div>
      <div class="pm-booking-amount">
        <div class="pm-amount-label">Total</div>
        <div class="pm-amount-value"  id="pmAmount">NPR 0</div>
      </div>
    </div>

    <!-- Body -->
    <div class="pm-body">

      <!-- Step indicators -->
      <div class="pm-steps" id="pmSteps">
        <div class="pm-step pm-step-active" data-step="1">
          <div class="pm-step-circle">1</div>
          <span>Choose</span>
        </div>
        <div class="pm-step-line" data-line="1-2"></div>
        <div class="pm-step" data-step="2">
          <div class="pm-step-circle">2</div>
          <span>Scan &amp; Pay</span>
        </div>
        <div class="pm-step-line" data-line="2-3"></div>
        <div class="pm-step" data-step="3">
          <div class="pm-step-circle">3</div>
          <span>Confirm</span>
        </div>
      </div>

      <!-- Payment method selection -->
      <div>
        <div class="pm-section-label">Payment Method</div>
        <div class="pm-method-group">

          <button class="pm-method-btn pm-esewa pm-active" id="pmEsewaBtn" aria-pressed="true">
            <img class="pm-method-logo" id="pmEsewaLogo" src="" alt="eSewa">
            <span class="pm-method-name">eSewa</span>
            <span class="pm-method-check" aria-hidden="true">
              <svg viewBox="0 0 12 10" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="1,5 4,8 11,1"/>
              </svg>
            </span>
          </button>

          <button class="pm-method-btn pm-khalti" id="pmKhaltiBtn" aria-pressed="false">
            <img class="pm-method-logo" id="pmKhaltiLogo" src="" alt="Khalti">
            <span class="pm-method-name">Khalti</span>
            <span class="pm-method-check" aria-hidden="true">
              <svg viewBox="0 0 12 10" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="1,5 4,8 11,1"/>
              </svg>
            </span>
          </button>

        </div>
      </div>

      <!-- QR code -->
      <div class="pm-qr-section">
        <div class="pm-qr-wrapper pm-qr-esewa" id="pmQrWrapper">
          <img class="pm-qr-img" id="pmQrImg" src="" alt="Payment QR Code">
        </div>
        <div class="pm-qr-instruction">
          <p id="pmQrInstruction">Open eSewa app → Scan QR → Confirm payment</p>
          <div class="pm-qr-step" id="pmQrStep">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <rect x="5" y="2" width="14" height="20" rx="2"/>
              <line x1="12" y1="18" x2="12" y2="18"/>
            </svg>
            Use the app to scan and pay
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="pm-divider">Enter Code After Payment</div>

      <!-- Transaction input -->
      <div class="pm-txn-group">
        <label class="pm-txn-label" for="pmTxnInput">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Transaction Code
        </label>
        <div class="pm-txn-input-row">
          <input
            class="pm-txn-input"
            id="pmTxnInput"
            type="text"
            placeholder="e.g. 0078TXN2026..."
            autocomplete="off"
            spellcheck="false"
          >
          <button class="pm-submit-btn" id="pmSubmitBtn" disabled>
            Submit
          </button>
        </div>
      </div>

      <!-- Payment status (hidden until submission) -->
      <div class="pm-status-area" id="pmStatusArea">

        <div class="pm-status-indicator" id="pmStatusIndicator">
          <span class="pm-status-dot"></span>
          <div class="pm-status-text-block">
            <div class="pm-status-title" id="pmStatusTitle">Processing…</div>
            <div class="pm-status-msg"   id="pmStatusMsg">Please wait</div>
          </div>
        </div>

        <div class="pm-txn-ref" id="pmTxnRef"></div>

        <button class="pm-done-btn" id="pmDoneBtn" style="display:none">
          🎉 Done — View My Bookings
        </button>

      </div>

    </div><!-- /pm-body -->
  </div><!-- /pm-modal -->
</div><!-- /pm-overlay -->
        `;

        const container = document.createElement('div');
        container.innerHTML = html.trim();
        document.body.appendChild(container.firstElementChild);
    }

    // ── Cache DOM refs ────────────────────────────────────────────────
    function cacheRefs() {
        overlay           = document.getElementById('pmOverlay');
        modal             = document.getElementById('pmModal');
        closeBtn          = document.getElementById('pmClose');
        esewaBtn          = document.getElementById('pmEsewaBtn');
        khaltiBtn         = document.getElementById('pmKhaltiBtn');
        qrImg             = document.getElementById('pmQrImg');
        qrWrapper         = document.getElementById('pmQrWrapper');
        txnInput          = document.getElementById('pmTxnInput');
        submitBtn         = document.getElementById('pmSubmitBtn');
        statusArea        = document.getElementById('pmStatusArea');
        doneBtn           = document.getElementById('pmDoneBtn');
        bookingActivity   = document.getElementById('pmActivity');
        bookingMeta       = document.getElementById('pmMeta');
        bookingAmount     = document.getElementById('pmAmount');
        stepDots          = document.querySelectorAll('.pm-step');
        stepLines         = document.querySelectorAll('.pm-step-line');

        // Load logos from assets
        if (typeof PAYMENT_ASSETS !== 'undefined') {
            document.getElementById('pmEsewaLogo').src  = PAYMENT_ASSETS.esewa.logo;
            document.getElementById('pmKhaltiLogo').src = PAYMENT_ASSETS.khalti.logo;
            qrImg.src = PAYMENT_ASSETS.esewa.qr;
        }
    }

    // ── Bind events ───────────────────────────────────────────────────
    function bindEvents() {
        // Close
        closeBtn.addEventListener('click', closeModal);
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) closeModal();
        });

        // Keyboard
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && state.isOpen) closeModal();
        });

        // Method buttons
        esewaBtn.addEventListener('click', function () { selectMethod('esewa'); });
        khaltiBtn.addEventListener('click', function () { selectMethod('khalti'); });

        // Transaction input
        txnInput.addEventListener('input', function () {
            state.txnCode = txnInput.value.trim();
            submitBtn.disabled = state.txnCode.length < 4;
        });

        // Submit
        submitBtn.addEventListener('click', handleSubmit);
        txnInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !submitBtn.disabled) handleSubmit();
        });

        // Done button
        doneBtn.addEventListener('click', function () {
            closeModal();
            // Switch to bookings section after a brief delay
            setTimeout(function () {
                if (typeof switchSection === 'function') {
                    switchSection('bookings', null);
                }
            }, 300);
        });
    }

    // ── Intercept the original Confirm Booking button ─────────────────
    function interceptBookForm() {
        var bookForm = document.getElementById('bookForm');
        if (!bookForm) return;

        var submitBtnEl = bookForm.querySelector('button[type="submit"], .btn-primary');
        if (!submitBtnEl) return;

        bookForm.addEventListener('submit', function (e) {
            var dateVal = document.getElementById('bookDate');
            if (!dateVal || !dateVal.value) {
                return;
            }

            e.preventDefault();

            var selected = document.querySelector('.activity-option.selected');
            var actName  = selected ? selected.getAttribute('data-name') : 'Adventure';
            var date     = dateVal.value;
            var people   = parseInt(document.getElementById('bookPeople').value) || 1;
            var totalEl  = document.getElementById('bookTotal');
            var totalStr = totalEl ? totalEl.textContent : 'NPR 0';
            var totalNum = parseInt(totalStr.replace(/[^0-9]/g, '')) || 0;

            state.booking = {
                activity: actName,
                date:     date,
                people:   people,
                total:    totalNum,
            };

            openModal();
        });
    }

    // ── Open / Close ──────────────────────────────────────────────────
    function openModal() {
        state.status   = null;
        state.txnCode  = '';
        txnInput.value = '';
        submitBtn.disabled = true;
        statusArea.classList.remove('pm-visible');
        doneBtn.style.display = 'none';
        selectMethod('esewa', true);
        setStep(1);

        bookingActivity.textContent = state.booking.activity;
        bookingMeta.textContent     = formatDate(state.booking.date) +
                                      ' · ' + state.booking.people +
                                      ' person' + (state.booking.people > 1 ? 's' : '');
        bookingAmount.textContent   = 'NPR ' + state.booking.total.toLocaleString();

        state.isOpen = true;
        overlay.classList.add('pm-open');
        document.body.style.overflow = 'hidden';

        setTimeout(function () { esewaBtn.focus(); }, 400);
    }

    function closeModal() {
        state.isOpen = false;
        overlay.classList.remove('pm-open');
        document.body.style.overflow = '';

        if (state.status === 'confirmed') {
            var form = document.getElementById('bookForm');
            if (form) {
                var paidInput = document.createElement('input');
                paidInput.type  = 'hidden';
                paidInput.name  = 'payment_done';
                paidInput.value = '1';
                form.appendChild(paidInput);
                form.submit();
            }
        }
    }

    // ── Method selection ──────────────────────────────────────────────
    function selectMethod(method, quiet) {
        if (state.method === method && !quiet) return;
        state.method = method;

        esewaBtn.classList.toggle('pm-active', method === 'esewa');
        khaltiBtn.classList.toggle('pm-active', method === 'khalti');
        esewaBtn.setAttribute('aria-pressed', method === 'esewa');
        khaltiBtn.setAttribute('aria-pressed', method === 'khalti');

        qrWrapper.className = 'pm-qr-wrapper pm-qr-' + method;

        switchQR(method);

        if (typeof PAYMENT_ASSETS !== 'undefined') {
            var assets = PAYMENT_ASSETS[method];
            document.getElementById('pmQrInstruction').textContent = assets.instructions;
        }

        if (!quiet) setStep(2);
    }

    function switchQR(method) {
        if (typeof PAYMENT_ASSETS === 'undefined') return;

        qrImg.classList.add('pm-qr-switching');
        setTimeout(function () {
            qrImg.src = PAYMENT_ASSETS[method].qr;
            qrImg.classList.remove('pm-qr-switching');
        }, 280);
    }

    // ── Step indicator ────────────────────────────────────────────────
    function setStep(n) {
        stepDots.forEach(function (dot) {
            var s = parseInt(dot.getAttribute('data-step'));
            dot.classList.remove('pm-step-active', 'pm-step-done');
            if (s < n)  dot.classList.add('pm-step-done');
            if (s === n) dot.classList.add('pm-step-active');
            var circle = dot.querySelector('.pm-step-circle');
            if (s < n) circle.innerHTML = '<svg viewBox="0 0 12 10" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="1,5 4,8 11,1"/></svg>';
            else circle.textContent = s;
        });
        stepLines.forEach(function (line) {
            var key = line.getAttribute('data-line');
            var from = parseInt(key.split('-')[0]);
            line.classList.toggle('pm-line-done', from < n);
        });
    }

    // ── Handle submit ─────────────────────────────────────────────────
    function handleSubmit() {
        if (state.txnCode.length < 4) return;

        submitBtn.classList.add('pm-loading');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Verifying';

        showStatus('pending', 'Verifying Payment…', 'Checking transaction with ' + PAYMENT_ASSETS[state.method].name);
        setStep(3);

        verifyPayment(state.txnCode, state.method, function (result) {
            submitBtn.classList.remove('pm-loading');
            submitBtn.textContent = 'Submit';

            if (result.success) {
                state.status = 'confirmed';
                showStatus('confirmed', 'Payment Confirmed!', 'Your adventure is officially booked 🎉');
                document.getElementById('pmTxnRef').innerHTML =
                    'Transaction Ref: <span>' + state.txnCode.toUpperCase() + '</span>';
                doneBtn.style.display = 'block';
                txnInput.disabled = true;
            } else {
                state.status = 'failed';
                showStatus('failed', 'Verification Failed', result.message || 'Please check your transaction code and retry.');
                submitBtn.disabled = false;
            }
        });
    }

    function showStatus(type, title, msg) {
        var indicator = document.getElementById('pmStatusIndicator');
        indicator.className = 'pm-status-indicator pm-' + type;
        document.getElementById('pmStatusTitle').textContent = title;
        document.getElementById('pmStatusMsg').textContent   = msg;
        statusArea.classList.add('pm-visible');
        statusArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // ── Mock payment verification (replace with real API) ─────────────
    // To integrate eSewa: POST to https://rc-epay.esewa.com.np/api/epay/transaction/status/
    // To integrate Khalti: POST to https://khalti.com/api/v2/payment/verify/
    function verifyPayment(code, method, callback) {
        setTimeout(function () {
            var validCodes = ['123456', 'TEST', 'THRILLSPHERE', 'KHALTI'];
            var upper = code.toUpperCase();
            var isValid = validCodes.some(function (v) { return upper.indexOf(v) !== -1; }) || code.length >= 8;

            if (isValid) {
                callback({ success: true, txnId: code });
            } else {
                callback({ success: false, message: 'Code not found. Try a transaction code with 8+ characters.' });
            }
        }, 1800);
    }

    // ── Helpers ───────────────────────────────────────────────────────
    function formatDate(dateStr) {
        if (!dateStr) return '—';
        try {
            var d = new Date(dateStr);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch (e) { return dateStr; }
    }

    // ── Expose openModal globally (for testing / custom triggers) ─────
    window.ThrillPayment = {
        open:  openModal,
        close: closeModal,
        state: state,
    };

    // ── Boot ─────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
