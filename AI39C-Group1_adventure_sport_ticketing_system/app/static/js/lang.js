/* ═══════════════════════════════════════════════════════
   lang.js — Thrill Sphere  |  Nepali ⇄ English Toggle
   ═══════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var LANG_KEY = 'ts_lang';

  var T = {
    /* ── LANG BUTTON ── */
    'lang.btn':                  { en: 'नेपाली',    ne: 'English' },

    /* ── NAVBAR ── */
    'nav.home':                  { en: 'Home',                   ne: 'गृहपृष्ठ' },
    'nav.dashboard':             { en: 'Dashboard',              ne: 'ड्यासबोर्ड' },
    'nav.wishlist':              { en: 'Wishlist',               ne: 'इच्छासूची' },
    'nav.profile':               { en: 'Profile',                ne: 'प्रोफाइल' },
    'nav.login':                 { en: 'Login',                  ne: 'लगिन' },
    'nav.register':              { en: 'Register',               ne: 'दर्ता गर्नुस्' },
    'nav.logout':                { en: 'Logout',                 ne: 'लगआउट' },

    /* ── FOOTER ── */
    'footer.tagline':            { en: "Kathmandu's premier adventure sports booking platform. We curate secure, certified, and unforgettable adrenaline-fueled experiences in Nepal.", ne: 'काठमाडौंको प्रमुख साहसिक खेल बुकिङ प्लेटफर्म। हामी नेपालमा सुरक्षित, प्रमाणित र अविस्मरणीय एड्रिनालिन अनुभवहरू प्रदान गर्छौं।' },
    'footer.adventures':         { en: 'Adventures',             ne: 'साहसिक खेलहरू' },
    'footer.pages':              { en: 'Pages',                  ne: 'पृष्ठहरू' },
    'footer.paragliding':        { en: 'Paragliding',            ne: 'प्याराग्लाइडिङ' },
    'footer.rafting':            { en: 'River Rafting',          ne: 'नदी र्याफ्टिङ' },
    'footer.trekking':           { en: 'Himalayan Trekking',     ne: 'हिमालयन ट्रेकिङ' },
    'footer.bungee':             { en: 'Bungee Jumping',         ne: 'बन्जी जम्पिङ' },
    'footer.my-wishlist':        { en: 'My Wishlist',            ne: 'मेरो इच्छासूची' },
    'footer.profile-mgmt':       { en: 'Profile Management',     ne: 'प्रोफाइल व्यवस्थापन' },
    'footer.home':               { en: 'Home',                   ne: 'गृहपृष्ठ' },
    'footer.dashboard':          { en: 'Dashboard',              ne: 'ड्यासबोर्ड' },
    'footer.copyright':          { en: '© 2026 Thrill Sphere. Kathmandu, Nepal. All rights reserved.', ne: '© २०२६ थ्रिल स्फियर। काठमाडौं, नेपाल। सर्वाधिकार सुरक्षित।' },
    'footer.licensed':           { en: 'Safety Licensed & Certified Agency', ne: 'सुरक्षा अनुमतिप्राप्त र प्रमाणित एजेन्सी' },

    /* ── HOME ── */
    'home.hero-tag':             { en: 'Adventure Travel — Kathmandu, Nepal', ne: 'साहसिक यात्रा — काठमाडौं, नेपाल' },
    'home.hero-title':           { en: 'Where Every<br><em>Thrill</em> Beckons', ne: 'जहाँ हरेक<br><em>रोमाञ्च</em> बोलाउँछ' },
    'home.hero-desc':            { en: "Nepal's premier adventure sports booking platform. We curate journeys that challenge limits and shape memories that endure a lifetime.", ne: 'नेपालको सर्वश्रेष्ठ साहसिक खेल बुकिङ प्लेटफर्म। हामी सीमाहरू चुनौती दिने र जीवनभर टिकने यादहरू बनाउने यात्राहरू सञ्चालन गर्छौं।' },
    'home.explore-activities':   { en: 'Explore Activities',     ne: 'गतिविधिहरू हेर्नुस्' },
    'home.book-trip':            { en: 'Book a Trip',            ne: 'यात्रा बुक गर्नुस्' },
    'home.what-we-offer':        { en: 'What We Offer',          ne: 'हाम्रो सेवाहरू' },
    'home.our-adventures':       { en: 'Our <em>Adventures</em>',ne: 'हाम्रा <em>साहसिक</em> खेलहरू' },
    'home.adventures-desc':      { en: 'Six world-class adventures curated with uncompromising safety standards and guided by local experts who call the Himalayas home.', ne: 'स्थानीय विशेषज्ञहरूद्वारा सञ्चालित विश्वस्तरीय छवटा साहसिक खेलहरू, अटुट सुरक्षा मानकसहित।' },
    'home.adv-sky':              { en: 'Sky',                    ne: 'आकाश' },
    'home.adv-water':            { en: 'Water',                  ne: 'पानी' },
    'home.adv-mountain':         { en: 'Mountain',               ne: 'पहाड' },
    'home.adv-extreme':          { en: 'Extreme',                ne: 'एक्स्ट्रिम' },
    'home.adv-aerial':           { en: 'Aerial',                 ne: 'हवाई' },
    'home.act-paragliding':      { en: 'Paragliding',            ne: 'प्याराग्लाइडिङ' },
    'home.act-rafting':          { en: 'River Rafting',          ne: 'नदी र्याफ्टिङ' },
    'home.act-trekking':         { en: 'Himalayan Trekking',     ne: 'हिमालयन ट्रेकिङ' },
    'home.act-bungee':           { en: 'Bungee Jumping',         ne: 'बन्जी जम्पिङ' },
    'home.act-ziplining':        { en: 'Zip-lining',             ne: 'जिप-लाइनिङ' },
    'home.stat-adventurers':     { en: 'Thrilled Adventurers',   ne: 'रोमाञ्चित साहसी' },
    'home.stat-activities':      { en: 'Epic Activities',        ne: 'शानदार गतिविधिहरू' },
    'home.stat-years':           { en: 'Years Operating',        ne: 'वर्षको अनुभव' },
    'home.stat-safety':          { en: '100% Safety Track Record', ne: '१००% सुरक्षा रेकर्ड' },
    'home.our-story-label':      { en: 'Our Story',              ne: 'हाम्रो कथा' },
    'home.our-story-title':      { en: 'Rooted in <em>Kathmandu,</em><br>Built for Adventure', ne: '<em>काठमाडौंमा</em> जरा गाडिएको,<br>साहसको लागि बनेको' },
    'home.story-1':              { en: 'Thrill Sphere was founded by a team of passionate explorers in Kathmandu — one of the world\'s most iconic gateways to the high Himalayas. We believe the mountain kingdom holds some of the world\'s most exhilarating adventures, and we aim to share them securely.', ne: 'थ्रिल स्फियरको स्थापना काठमाडौंका जोशिला अन्वेषकहरूको टोलीले गरेको थियो — उच्च हिमालयको विश्वको सबैभन्दा प्रतिष्ठित प्रवेशद्वारमध्ये एक। हाम्रो विश्वास छ कि यो पहाडी राज्यमा विश्वका केही सबैभन्दा रोमाञ्चक साहसहरू छन्।' },
    'home.story-2':              { en: 'Every trip is engineered with deep local expertise, certified safety gear, and genuine support for both our guests and the environment we explore in.', ne: 'प्रत्येक यात्रा गहिरो स्थानीय विशेषज्ञता, प्रमाणित सुरक्षा उपकरण, र हाम्रा पाहुनाहरू र वातावरण दुवैको लागि वास्तविक समर्थनसहित तयार गरिएको छ।' },
    'home.feature-location':     { en: 'Thamel, Kathmandu, Bagmati Province, Nepal', ne: 'थमेल, काठमाडौं, बागमती प्रदेश, नेपाल' },
    'home.feature-guides':       { en: 'Government-licensed guides & certified safety protocols', ne: 'सरकारी अनुमतिप्राप्त गाइड र प्रमाणित सुरक्षा प्रोटोकलहरू' },
    'home.feature-eco':          { en: 'Eco-conscious booking models for sustainable tourism', ne: 'दिगो पर्यटनका लागि पर्यावरण-सचेत बुकिङ मोडेलहरू' },
    'home.explore-challenges':   { en: 'Explore Challenges',     ne: 'चुनौतीहरू अन्वेषण गर्नुस्' },
    'home.gallery-label':        { en: 'Gallery',                ne: 'ग्यालेरी' },
    'home.gallery-title':        { en: 'Moments <em>Captured</em>', ne: 'कैद गरिएका <em>क्षणहरू</em>' },
    'home.testimonials-label':   { en: 'Client Stories',         ne: 'ग्राहकका कथाहरू' },
    'home.testimonials-title':   { en: 'What Our <em>Adventurers</em> Say', ne: 'हाम्रा <em>साहसीहरू</em> के भन्छन्' },
    'home.testimonial-1':        { en: '"The views above Kathmandu Valley were simply breathtaking. The Thrill Sphere team was professional throughout and made me feel completely safe. I will absolutely book again."', ne: '"काठमाडौं उपत्यका माथिका दृश्यहरू अचम्मको थिए। थ्रिल स्फियर टोली सम्पूर्ण समयमा व्यावसायिक थियो र मलाई पूर्ण रूपमा सुरक्षित महसुस गराइयो।"' },
    'home.testimonial-2':        { en: '"The Trishuli rapids were incredible. Our guide kept the energy high the entire day. The riverside lunch was a wonderful touch — I have already recommended this to everyone I know."', ne: '"त्रिशूली र्याफ्टिङ अद्भुत थियो। हाम्रो गाइडले दिनभर ऊर्जा उच्च राखे। नदी किनारको खाना अद्भुत स्पर्श थियो।"' },
    'home.testimonial-3':        { en: '"Three unforgettable days walking through the Annapurna highlands. Our guide had encyclopaedic knowledge of the region. The camping was comfortable and exceptionally well-organised."', ne: '"अन्नपूर्ण उच्चभूमिमा हिँडेका तीन अविस्मरणीय दिनहरू। हाम्रो गाइडसँग क्षेत्रको विश्वकोशीय ज्ञान थियो।"' },
    'home.reviewer-paragliding': { en: 'Paragliding',            ne: 'प्याराग्लाइडिङ' },
    'home.reviewer-rafting':     { en: 'River Rafting',          ne: 'नदी र्याफ्टिङ' },
    'home.reviewer-trekking':    { en: 'Trekking',               ne: 'ट्रेकिङ' },
    'home.map-label':            { en: 'MAP — Kathmandu, Nepal', ne: 'नक्शा — काठमाडौं, नेपाल' },
    'home.find-us':              { en: 'Find Us',                ne: 'हामीलाई खोज्नुस्' },
    'home.visit-office':         { en: 'Visit Our <em>Office</em>', ne: 'हाम्रो <em>कार्यालय</em> भ्रमण गर्नुस्' },
    'home.address':              { en: 'Thamel, Kathmandu-29, Bagmati Province, Nepal', ne: 'थमेल, काठमाडौं-२९, बागमती प्रदेश, नेपाल' },
    'home.hours':                { en: 'Sun – Fri · 8:00 AM – 6:00 PM', ne: 'आइत – शुक्र · बिहान ८:०० – साँझ ६:००' },
    'home.book-appointment':     { en: 'Book an Appointment',    ne: 'अपोइन्टमेन्ट बुक गर्नुस्' },
    'home.safety-checked':       { en: 'Safety Checked',         ne: 'सुरक्षा जाँच गरिएको' },

    /* ── DASHBOARD ── */
    'dash.welcome-back':         { en: 'Welcome back',           ne: 'फेरि स्वागत छ' },
    'dash.tab-overview':         { en: 'Overview',               ne: 'अवलोकन' },
    'dash.tab-bookings':         { en: 'My Bookings',            ne: 'मेरा बुकिङहरू' },
    'dash.tab-book-new':         { en: 'Book Activity',          ne: 'गतिविधि बुक गर्नुस्' },
    'dash.stat-total':           { en: 'Total Bookings',         ne: 'कुल बुकिङहरू' },
    'dash.stat-upcoming':        { en: 'Upcoming',               ne: 'आगामी' },
    'dash.stat-completed':       { en: 'Completed',              ne: 'पूरा भएका' },
    'dash.stat-spent':           { en: 'Total Spent',            ne: 'कुल खर्च' },
    'dash.recent-adventures':    { en: 'Recent Adventures',      ne: 'हालका साहसहरू' },
    'dash.view-all':             { en: 'View All →',             ne: 'सबै हेर्नुस् →' },
    'dash.no-adventures':        { en: 'No adventures yet — book your first thrill!', ne: 'अहिलेसम्म कुनै साहस छैन — आफ्नो पहिलो रोमाञ्च बुक गर्नुस्!' },
    'dash.quick-book':           { en: 'Quick Book',             ne: 'द्रुत बुक' },
    'dash.all-activities':       { en: 'All Activities →',       ne: 'सबै गतिविधिहरू →' },
    'dash.my-bookings':          { en: 'My Bookings',            ne: 'मेरा बुकिङहरू' },
    'dash.filter-all':           { en: 'All',                    ne: 'सबै' },
    'dash.filter-upcoming':      { en: 'Upcoming',               ne: 'आगामी' },
    'dash.filter-completed':     { en: 'Completed',              ne: 'पूरा भएका' },
    'dash.no-bookings-title':    { en: 'No adventures booked yet.', ne: 'अहिलेसम्म कुनै साहस बुक भएको छैन।' },
    'dash.no-bookings-desc':     { en: 'The mountains are calling — book your first thrill!', ne: 'पहाडहरू बोलाउँदैछन् — आफ्नो पहिलो रोमाञ्च बुक गर्नुस्!' },
    'dash.explore-activities':   { en: 'Explore Activities',     ne: 'गतिविधिहरू हेर्नुस्' },
    'dash.book-adventure':       { en: 'Book an Adventure',      ne: 'साहस बुक गर्नुस्' },
    'dash.adventure-date':       { en: 'Adventure Date',         ne: 'साहसको मिति' },
    'dash.num-people':           { en: 'Number of People',       ne: 'व्यक्तिहरूको संख्या' },
    'dash.estimated-total':      { en: 'Estimated Total',        ne: 'अनुमानित जम्मा' },
    'dash.confirm-booking':      { en: 'Confirm Booking',        ne: 'बुकिङ पुष्टि गर्नुस्' },
    'dash.confirmed':            { en: 'Confirmed',              ne: 'पुष्टि भएको' },
    'dash.completed':            { en: 'Completed',              ne: 'पूरा भएको' },

    /* ── WISHLIST ── */
    'wish.saved-tag':            { en: 'Saved Adventures',       ne: 'सुरक्षित साहसहरू' },
    'wish.page-title':           { en: 'My Wishlist',            ne: 'मेरो इच्छासूची' },
    'wish.subtitle':             { en: 'Keep track of your favorite thrill-seeking experiences in Nepal. Book them when you\'re ready to answer the call of the mountains.', ne: 'नेपालमा तपाईंका मनपर्ने रोमाञ्चक अनुभवहरू ट्र्याक गर्नुस्। पहाडको बोलावट सुन्न तयार हुँदा बुक गर्नुस्।' },
    'wish.safety-checked':       { en: 'Safety Checked',         ne: 'सुरक्षा जाँच गरिएको' },
    'wish.seats-available':      { en: 'Seats Available',        ne: 'सिटहरू उपलब्ध' },
    'wish.tickets-left':         { en: 'tickets left',           ne: 'टिकटहरू बाँकी' },
    'wish.hurry':                { en: 'Hurry! Only',            ne: 'हतार गर्नुस्! केवल' },
    'wish.price-per':            { en: 'Price per person',       ne: 'प्रति व्यक्ति मूल्य' },
    'wish.remove':               { en: 'Remove',                 ne: 'हटाउनुस्' },
    'wish.book-now':             { en: 'Book Now',               ne: 'अहिले बुक गर्नुस्' },
    'wish.empty-title':          { en: 'Your Wishlist is Empty', ne: 'तपाईंको इच्छासूची खाली छ' },
    'wish.empty-desc':           { en: "You haven't saved any epic journeys yet. Head back to our challenges deck and find your next rush!", ne: 'तपाईंले अहिलेसम्म कुनै शानदार यात्रा सुरक्षित गर्नुभएको छैन। हाम्रो चुनौती पृष्ठमा फर्कनुस् र आफ्नो अर्को रोमाञ्च खोज्नुस्!' },
    'wish.explore-challenges':   { en: 'Explore Challenges',     ne: 'चुनौतीहरू अन्वेषण गर्नुस्' },

    /* ── LOGIN ── */
    'login.title':               { en: 'Login',                  ne: 'लगिन' },
    'login.btn':                 { en: 'Login',                  ne: 'लगिन गर्नुस्' },
    'login.no-account':          { en: "Don't have an account?", ne: 'खाता छैन?' },
    'login.register-btn':        { en: 'Register',               ne: 'दर्ता गर्नुस्' },
    'login.google-btn':          { en: 'Continue with Google',   ne: 'गुगलसँग जारी राख्नुस्' },
    'login.forgot':              { en: 'Forgot password?',       ne: 'पासवर्ड बिर्सनुभयो?' },

    /* ── REGISTER ── */
    'register.title':            { en: 'Register',               ne: 'दर्ता गर्नुस्' },
    'register.btn':              { en: 'Register',               ne: 'दर्ता गर्नुस्' },
    'register.have-account':     { en: 'Already have an account?', ne: 'पहिले नै खाता छ?' },
    'register.login-btn':        { en: 'Login',                  ne: 'लगिन गर्नुस्' },

    /* ── RESET ── */
    'reset.title':               { en: 'Reset Password',         ne: 'पासवर्ड रिसेट गर्नुस्' },
    'reset.send-otp':            { en: 'Send Code',              ne: 'कोड पठाउनुस्' },
    'reset.reset-btn':           { en: 'Reset Password',         ne: 'पासवर्ड रिसेट गर्नुस्' },
    'reset.back-login':          { en: 'Back to Login',          ne: 'लगिनमा फर्कनुस्' },

    /* ── PROFILE ── */
    'profile.title':             { en: 'Manage Profile',         ne: 'प्रोफाइल व्यवस्थापन' },
    'profile.save':              { en: 'Save Changes',           ne: 'परिवर्तनहरू सुरक्षित गर्नुस्' },
  };

  function getLang()         { return localStorage.getItem(LANG_KEY) || 'en'; }
  function setLang(lang)     { localStorage.setItem(LANG_KEY, lang); }
  function translate(key, lang) {
    var e = T[key];
    return e ? (e[lang] || e['en']) : null;
  }

  function applyLang(lang) {
    /* innerHTML elements */
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = translate(el.getAttribute('data-i18n'), lang);
      if (v !== null) el.innerHTML = v;
    });
    /* placeholder elements */
    document.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
      var v = translate(el.getAttribute('data-i18n-ph'), lang);
      if (v !== null) el.placeholder = v;
    });
    /* button label */
    var btn = document.getElementById('langToggleBtn');
    if (btn) btn.textContent = translate('lang.btn', lang) || (lang === 'en' ? 'नेपाली' : 'English');
    document.documentElement.lang = lang === 'ne' ? 'ne' : 'en';
  }

  function toggle() {
    var next = getLang() === 'en' ? 'ne' : 'en';
    setLang(next);
    applyLang(next);
  }

  function init() {
    applyLang(getLang());
    var btn = document.getElementById('langToggleBtn');
    if (btn) btn.addEventListener('click', toggle);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.ThrillLang = { toggle: toggle, getLang: getLang, applyLang: applyLang };
})();
