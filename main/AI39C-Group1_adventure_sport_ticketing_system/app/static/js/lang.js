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

    /* ── BASE & NAVBAR ── */
    'nav.explore':               { en: 'Explore',                ne: 'अन्वेषण' },
    'nav.events':                { en: 'Events',                 ne: 'घटनाहरू' },
    'nav.gallery':               { en: 'Gallery',                ne: 'ग्यालेरी' },
    'nav.reviews':               { en: 'Reviews',                ne: 'समीक्षाहरू' },
    'nav.search-ph':             { en: 'Search adventures...',   ne: 'साहसिक यात्रा खोज्नुस्...' },

    /* ── DASHBOARD DYNAMIC & MISSING ── */
    'dash.good-morning':         { en: 'Good morning',           ne: 'शुभ प्रभात' },
    'dash.good-afternoon':       { en: 'Good afternoon',         ne: 'शुभ दिन' },
    'dash.good-evening':         { en: 'Good evening',           ne: 'शुभ साँझ' },
    'dash.tab-calendar':         { en: 'Calendar',               ne: 'पात्रो' },
    'dash.tab-notifications':    { en: 'Notifications',           ne: 'सूचनाहरू' },
    'dash.tab-profile':          { en: 'My Profile',             ne: 'मेरो प्रोफाइल' },
    'dash.member-since':         { en: 'Member since',           ne: 'देखि सदस्य' },
    'dash.people-label':         { en: 'person(s)',              ne: 'जना' },
    'dash.cancelled':            { en: 'Cancelled',              ne: 'रद्द गरिएको' },
    'dash.filter-cancelled':     { en: 'Cancelled',              ne: 'रद्द गरिएका' },
    'dash.cancel-btn':           { en: 'Cancel',                 ne: 'रद्द गर्नुस्' },
    'dash.book-now':             { en: 'Book Now',               ne: 'अहिले बुक गर्नुस्' },
    'dash.person-1':             { en: '1 person',               ne: '१ जना' },
    'dash.person-2':             { en: '2 people',               ne: '२ जना' },
    'dash.person-3':             { en: '3 people',               ne: '३ जना' },
    'dash.person-4':             { en: '4 people',               ne: '४ जना' },
    'dash.person-5':             { en: '5 people',               ne: '५ जना' },
    'dash.calendar-title':       { en: 'Adventure Calendar',     ne: 'साहसिक पात्रो' },
    'dash.day-sun':              { en: 'Sun',                    ne: 'आइत' },
    'dash.day-mon':              { en: 'Mon',                    ne: 'सोम' },
    'dash.day-tue':              { en: 'Tue',                    ne: 'मंगल' },
    'dash.day-wed':              { en: 'Wed',                    ne: 'बुध' },
    'dash.day-thu':              { en: 'Thu',                    ne: 'बिही' },
    'dash.day-fri':              { en: 'Fri',                    ne: 'शुक्र' },
    'dash.day-sat':              { en: 'Sat',                    ne: 'शनि' },
    'dash.sold-out':             { en: 'Sold Out',               ne: 'सबै बुक भएको' },
    'dash.selected':             { en: 'Selected',               ne: 'चयन गरिएको' },
    'dash.cal-select-date':      { en: 'Select a date to view events', ne: 'घटनाहरू हेर्न मिति चयन गर्नुहोस्' },
    'dash.cal-click-date':       { en: 'Click any highlighted date to explore upcoming adventure events', ne: 'आगामी साहसिक घटनाहरू अन्वेषण गर्न कुनै पनि हाइलाइट गरिएको मितिमा क्लिक गर्नुहोस्' },
    'dash.cal-no-bookings':      { en: 'No bookings on this date.', ne: 'यस मितिमा कुनै बुकिङ छैन।' },
    'dash.profile-title':        { en: 'My Profile',             ne: 'मेरो प्रोफाइल' },
    'dash.adventure-seeker':     { en: 'Adventure Seeker',       ne: 'साहसिक यात्री' },
    'dash.badge-trekker':        { en: 'Trekker',                ne: 'ट्रेकर' },
    'dash.badge-skydiver':       { en: 'Sky Diver',              ne: 'स्काई डाइभर' },
    'dash.badge-riverrunner':    { en: 'River Runner',           ne: 'रिभर रनर' },
    'dash.badge-thrillseeker':   { en: 'Thrill Seeker',          ne: 'थ्रिल सीकर' },
    'dash.full-name':            { en: 'Full Name',              ne: 'पूरा नाम' },
    'dash.email':                { en: 'Email',                  ne: 'इमेल' },
    'dash.phone':                { en: 'Phone',                  ne: 'फोन' },
    'dash.location':             { en: 'Location',               ne: 'स्थान' },
    'dash.member-since-label':   { en: 'Member Since',           ne: 'सदस्यता मिति' },
    'dash.account-status':       { en: 'Account Status',         ne: 'खाता स्थिति' },
    'dash.active':               { en: '✓ Active',               ne: '✓ सक्रिय' },
    'dash.edit-profile':         { en: 'Edit Profile',           ne: 'प्रोफाइल सम्पादन' },
    'dash.adventure-stats':      { en: 'Adventure Stats',        ne: 'साहसिक तथ्याङ्क' },
    'dash.stat-favourite':       { en: 'Favourite',              ne: 'मनपर्ने' },
    'dash.stat-mostvisited':     { en: 'Most Visited',           ne: 'सबैभन्दा धेरै भ्रमण गरिएको' },
    'dash.stat-peoplebrought':   { en: 'People Brought',         ne: 'साथमा ल्याएका व्यक्तिहरू' },
    'dash.your-notifications':   { en: 'Your Notifications',     ne: 'तपाईंका सूचनाहरू' },
    'dash.mark-read':            { en: 'Mark Read',              ne: 'पढेको चिन्ह लगाउनुस्' },
    'dash.no-notifications':     { en: 'You have no notifications at this time.', ne: 'तपाईंसँग यस समयमा कुनै सूचना छैन।' },

    /* ── EVENTS PAGE ── */
    'events.gatherings-tag':     { en: 'Thrill Gatherings',      ne: 'थ्रिल भेलाहरू' },
    'events.title':              { en: 'Epic Events & Challenges', ne: 'शानदार घटनाहरू र चुनौतीहरू' },
    'events.desc':               { en: "Join Nepal's premier adventure sport tournaments, outdoor music festivals, and community challenges. Book your spot today!", ne: 'नेपालको प्रमुख साहसिक खेल प्रतियोगिताहरू, बाहिरी संगीत उत्सवहरू, र सामुदायिक चुनौतीहरूमा सामेल हुनुहोस्। आज आफ्नो स्थान सुरक्षित गर्नुहोस्!' },
    'events.trending-featured':  { en: '🔥 Trending & Featured', ne: '🔥 ट्रेन्डिङ र विशेष' },
    'events.grid-view':          { en: 'Grid Explorer',          ne: 'ग्रिड अन्वेषक' },
    'events.timeline-view':      { en: 'Weekly Timeline Planner', ne: 'साप्ताहिक समयरेखा योजनाकार' },
    'events.timeline-title':     { en: 'Weekly Schedule Overview', ne: 'साप्ताहिक तालिका अवलोकन' },
    'events.timeline-desc':      { en: 'Click a day to view adventures scheduled for that day', ne: 'त्यस दिनको लागि निर्धारित साहसिक कार्यहरू हेर्न दिनमा क्लिक गर्नुहोस्' },
    'events.filter-search-label':{ en: 'Search Events',          ne: 'घटनाहरू खोज्नुहोस्' },
    'events.filter-search-ph':   { en: 'Type name or place...',  ne: 'नाम वा ठाउँ टाइप गर्नुहोस्...' },
    'events.filter-category-label':{ en: 'Category',            ne: 'श्रेणी' },
    'events.filter-location-label':{ en: 'Location',            ne: 'स्थान' },
    'events.filter-location-all':{ en: 'All Locations',          ne: 'सबै स्थानहरू' },
    'events.filter-date-label':  { en: 'Date Range',             ne: 'मिति दायरा' },
    'events.filter-price-label': { en: 'Max Price',              ne: 'अधिकतम मूल्य' },
    'events.filter-reset':       { en: 'Reset Filters',          ne: 'फिल्टरहरू रिसेट गर्नुहोस्' },
    'events.sort-by':            { en: 'Sort By',                ne: 'क्रमबद्ध गर्नुहोस्' },
    'events.sort-upcoming':      { en: 'Upcoming',               ne: 'आगामी' },
    'events.sort-price-asc':     { en: 'Price: Low-High',        ne: 'मूल्य: कम-उच्च' },
    'events.sort-price-desc':    { en: 'Price: High-Low',       ne: 'मूल्य: उच्च-कम' },
    'events.sort-popularity':    { en: 'Popularity',             ne: 'लोकप्रियता' },
    'events.view-details':       { en: 'View Details',           ne: 'विवरण हेर्नुहोस्' },
    'events.empty-title':        { en: 'No Events Available',    ne: 'कुनै घटना उपलब्ध छैन' },
    'events.empty-desc':         { en: 'Currently, there are no published events in the catalog. Check back later!', ne: 'हाल सूचीमा कुनै भी प्रकाशित घटनाहरू छैनन्। पछि फेरि जाँच गर्नुहोस्!' },
    'events.modal-desc-title':   { en: 'Description',            ne: 'विवरण' },
    'events.modal-details-title':{ en: 'Details',                ne: 'विवरणहरू' },
    'events.modal-category-label':{ en: 'Category',              ne: 'श्रेणी' },
    'events.modal-location-label':{ en: 'Location',              ne: 'स्थान' },
    'events.modal-date-label':   { en: 'Date & Time',            ne: 'मिति र समय' },
    'events.modal-duration-label':{ en: 'Duration',              ne: 'अवधि' },
    'events.modal-availability-label':{ en: 'Availability',      ne: 'उपलब्धता' },
    'events.modal-secure-tickets':{ en: 'Secure Tickets',        ne: 'टिकटहरू सुरक्षित गर्नुहोस्' },
    'events.modal-event-date':   { en: 'Event Date',             ne: 'घटनाको मिति' },
    'events.modal-num-tickets':  { en: 'Number of Tickets',      ne: 'टिकट संख्या' },
    'events.modal-total-amount': { en: 'Total Amount',           ne: 'कुल रकम' },
    'events.modal-confirm-btn':  { en: 'Confirm Booking',        ne: 'बुकिङ पुष्टि गर्नुहोस्' },

    /* ── GALLERY PAGE ── */
    'gallery.hero-tag':          { en: '📸 Adventure Shots',     ne: '📸 साहसिक तस्बिरहरू' },
    'gallery.hero-title':        { en: 'Our Gallery',            ne: 'हाम्रो ग्यालेरी' },
    'gallery.hero-desc':         { en: 'Real moments captured by our team — from soaring peaks to roaring rapids.', ne: 'हाम्रो टोलीले खिचेका वास्तविक क्षणहरू — उड्ने चुचुराहरूदेखि गर्जने नदीहरू सम्म।' },
    'gallery.admin-upload-title':{ en: 'Upload New Post',        ne: 'नयाँ पोस्ट अपलोड गर्नुहोस्' },
    'gallery.admin-badge':       { en: 'ADMIN',                  ne: 'प्रशासक' },
    'gallery.form-title-label':  { en: 'Post Title',             ne: 'पोस्ट शीर्षक' },
    'gallery.form-title-ph':     { en: 'e.g. Sunset Paragliding over Pokhara', ne: 'जस्तै: पोखरामा सूर्यास्त प्याराग्लाइडिङ' },
    'gallery.form-image-label':  { en: 'Image',                  ne: 'तस्बिर' },
    'gallery.drag-drop-1':       { en: 'Drag & drop or',         ne: 'ड्र्याग र ड्रप गर्नुहोस् वा' },
    'gallery.drag-drop-2':       { en: 'click to browse',        ne: 'ब्राउज गर्न क्लिक गर्नुहोस्' },
    'gallery.form-desc-label':   { en: 'Description (optional)', ne: 'विवरण (वैकल्पिक)' },
    'gallery.form-desc-ph':      { en: 'Share the story behind this shot...', ne: 'यस तस्बिरको पछाडिको कथा साझा गर्नुहोस्...' },
    'gallery.form-submit':       { en: 'Publish to Gallery',     ne: 'ग्यालेरीमा प्रकाशित गर्नुहोस्' },
    'gallery.delete-btn':        { en: 'Delete',                 ne: 'हटाउनुहोस्' },
    'gallery.empty-title':       { en: 'No Posts Yet',           ne: 'अहिलेसम्म कुनै पोस्ट छैन' },
    'gallery.empty-desc-admin':  { en: 'Use the panel above to upload your first adventure photo!', ne: 'आफ्नो पहिलो साहसिक फोटो अपलोड गर्न माथिको प्यानल प्रयोग गर्नुहोस्!' },
    'gallery.empty-desc-user':   { en: 'Check back soon — our team is capturing amazing moments!', ne: 'चाँडै पुन: जाँच गर्नुहोस् — हाम्रो टोलीले उत्कृष्ट क्षणहरू कैद गर्दैछ!' },

    /* ── REVIEWS PAGE ── */
    'reviews.hero-tag':          { en: '⭐ Adventurer Reviews',   ne: '⭐ साहसी समीक्षाहरू' },
    'reviews.hero-title':        { en: 'Adventure Reviews',      ne: 'साहसिक समीक्षाहरू' },
    'reviews.hero-desc':         { en: 'Real experiences from real thrill-seekers. Your voice shapes the next adventure.', ne: 'वास्तविक साहसीहरूबाट वास्तविक अनुभवहरू। तपाईंको आवाजले अर्को साहसिक कार्यलाई आकार दिन्छ।' },
    'reviews.edit-btn':          { en: '✏️ Edit',                ne: '✏️ सम्पादन' },
    'reviews.delete-btn':        { en: '🗑️ Delete',              ne: '🗑️ हटाउनुहोस्' },
    'reviews.empty-title':       { en: 'No Reviews Yet',         ne: 'अहिलेसम्म कुनै समीक्षा छैन' },
    'reviews.empty-desc':        { en: 'Be the first to share your Thrill Sphere experience!', ne: 'थ्रिल स्फियरको आफ्नो अनुभव साझा गर्ने पहिलो हुनुहोस्!' },
    'reviews.form-title':        { en: 'Share Your Experience',  ne: 'आफ्नो अनुभव साझा गर्नुहोस्' },
    'reviews.form-desc':         { en: 'Your honest review helps others plan their adventure.', ne: 'तपाईंको इमानदार समीक्षाले अरूलाई आफ्नो साहसिक कार्य योजना बनाउन मद्दत गर्दछ।' },
    'reviews.form-activity-label':{ en: 'Activity',              ne: 'गतिविधि' },
    'reviews.form-choose-activity':{ en: '— Choose Activity —',  ne: '— गतिविधि छान्नुहोस् —' },
    'reviews.form-rating-label': { en: 'Your Rating',            ne: 'तपाईंको मूल्याङ्कन' },
    'reviews.form-text-label':   { en: 'Your Review',            ne: 'तपाईंको समीक्षा' },
    'reviews.form-text-ph':      { en: 'Tell us about your adventure — the highs, thrills, and memories!', ne: 'हामीलाई तपाईंको साहसिक कार्यको बारेमा बताउनुहोस् — उच्च बिन्दुहरू, थ्रिलहरू, र सम्झनाहरू!' },
    'reviews.form-submit':       { en: 'Submit Review ⭐',       ne: 'समीक्षा बुझाउनुहोस् ⭐' },
    'reviews.login-required':    { en: 'You must be logged in to leave a review.', ne: 'समीक्षा छोड्नको लागि तपाईं लगइन हुनुपर्छ।' },
    'reviews.login-link':        { en: 'Log In',                 ne: 'लगइन गर्नुहोस्' },
    'reviews.login-or':          { en: 'or',                     ne: 'वा' },
    'reviews.signup-link':       { en: 'Sign Up',                ne: 'दर्ता गर्नुहोस्' },
    'reviews.modal-title':       { en: '✏️ Edit Your Review',    ne: '✏️ आफ्नो समीक्षा सम्पादन गर्नुहोस्' },
    'reviews.modal-rating-label':{ en: 'Update Rating',          ne: 'मूल्याङ्कन अद्यावधिक गर्नुहोस्' },
    'reviews.modal-text-label':  { en: 'Review Text',            ne: 'समीक्षा पाठ' },
    'reviews.modal-text-ph':     { en: 'Update your review...',  ne: 'आफ्नो समीक्षा अद्यावधिक गर्नुहोस्...' },
    'reviews.modal-cancel':      { en: 'Cancel',                 ne: 'रद्द गर्नुहोस्' },
    'reviews.modal-save':        { en: 'Save Changes',           ne: 'परिवर्तनहरू सुरक्षित गर्नुहोस्' },

    /* ── ACTIVITY PAGE ── */
    'activity.duration':         { en: 'Duration',               ne: 'अवधि' },
    'activity.location':         { en: 'Location',               ne: 'स्थान' },
    'activity.price':            { en: 'Price',                  ne: 'मूल्य' },
    'activity.difficulty':       { en: 'Difficulty',             ne: 'कठिनाई स्तर' },
    'activity.book-now':         { en: 'Book Now',               ne: 'अहिले बुक गर्नुस्' },
    'activity.login-to-book':    { en: 'Login to Book',          ne: 'बुकिङका लागि लगिन गर्नुस्' },

    /* ── EVENT DETAIL PAGE ── */
    'event-detail.back':         { en: 'Back to Events',         ne: 'घटनाहरूमा फर्कनुस्' },
    'event-detail.saved-wishlist':{ en: 'Saved to Wishlist',     ne: 'इच्छासूचीमा सुरक्षित भयो' },
    'event-detail.add-wishlist': { en: 'Add to Wishlist',        ne: 'इच्छासूचीमा थप्नुहोस्' },
    'event-detail.overview-title':{ en: 'Adventure Overview',    ne: 'साहसिक अवलोकन' },
    'event-detail.organizer-title':{ en: 'Organizer Information',ne: 'आयोजकको जानकारी' },
    'event-detail.organizer-subtitle':{ en: 'Official Host & Safety Coordinator', ne: 'आधिकारिक आयोजक र सुरक्षा संयोजक' },
    'event-detail.location-title':{ en: 'Event Location',        ne: 'घटनाको स्थान' },
    'event-detail.venue-note':   { en: '(Venue details will be sent in ticket confirmation)', ne: '(स्थानको विस्तृत विवरण टिकट पुष्टिकरणमा पठाइनेछ)' },
    'event-detail.ticket-price': { en: 'Ticket Price',           ne: 'टिकट मूल्य' },
    'event-detail.availability-status':{ en: 'Availability Status',ne: 'उपलब्धता स्थिति' },
    'event-detail.seats-left-label':{ en: 'seats left',          ne: 'सिटहरू बाँकी' },
    'event-detail.choose-date':  { en: 'Choose Date',            ne: 'मिति छान्नुहोस्' },
    'event-detail.date-note':    { en: 'This event takes place on a specific scheduled day.', ne: 'यो घटना निश्चित निर्धारित दिनमा मात्र सञ्चालन हुन्छ।' },
    'event-detail.num-tickets':  { en: 'Number of Tickets',      ne: 'टिकट संख्या' },
    'event-detail.total-price':  { en: 'Total Price',            ne: 'कुल मूल्य' },
    'event-detail.sold-out':     { en: 'Sold Out',               ne: 'सबै बुक भएको' },
    'event-detail.confirm-booking':{ en: 'Confirm Booking',      ne: 'बुकिङ पुष्टि गर्नुहोस्' },

    /* ── EVENTS DYNAMIC STRINGS ── */
    'events.tickets-from':       { en: 'Tickets from',           ne: 'टिकट सुरु मूल्य' },
    'events.book-spot':          { en: 'Book Spot',              ne: 'स्थान सुरक्षित गर्नुस्' },
    'events.live-today':         { en: 'Live Today',             ne: 'आज प्रत्यक्ष' },
    'events.no-results-title':   { en: 'No Matching Events Found', ne: 'कुनै मिल्दो घटना फेला परेन' },
    'events.no-results-desc':    { en: 'Try broadening your search term or adjusting filter values.', ne: 'खोज शब्द विस्तृत गर्ने प्रयास गर्नुहोस् वा फिल्टर मानहरू समायोजन गर्नुहोस्।' },
    'events.error-title':        { en: 'Oops! Something went wrong', ne: 'ओहो! केहि गलत भयो' },
    'events.error-desc':         { en: 'Failed to retrieve challenges. Please try reloading or check your internet connection.', ne: 'चुनौतीहरू पुनःप्राप्त गर्न असफल भयो। कृपया पुन: लोड गर्ने प्रयास गर्नुहोस् वा इन्टरनेट जडान जाँच गर्नुहोस्।' },
    'events.timeline-empty-title':{ en: 'No Events Scheduled',    ne: 'कुनै घटना तालिकाबद्ध छैन' },
    'events.timeline-empty-desc': { en: 'There are no upcoming adventure events in our database at this moment.', ne: 'यस समयमा हाम्रो डाटाबेसमा कुनै आगामी साहसिक घटनाहरू छैनन्।' },
    'events.timeline-no-adventures-title':{ en: 'No Adventures Scheduled', ne: 'कुनै साहसिक कार्य तालिकाबद्ध छैन' },
    'events.timeline-no-adventures-desc':{ en: 'There are no organized trips scheduled for this date. Check out other dates or click below to view the full upcoming weekly schedule.', ne: 'यस मितिका लागि कुनै संगठित यात्राहरू तय गरिएको छैन। अन्य मितिहरू जाँच गर्नुहोस् वा तल क्लिक गरेर पूरा साप्ताहिक तालिका हेर्नुहोस्।' },
    'events.timeline-view-all':  { en: 'View All Days',          ne: 'सबै दिनहरू हेर्नुहोस्' }
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

    // Dispatch a custom event so other components (like calendar & dashboard) can react
    var event = new CustomEvent('languagechange', { detail: { lang: lang } });
    window.dispatchEvent(event);
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

  window.ThrillLang = { toggle: toggle, getLang: getLang, applyLang: applyLang, translate: translate };
})();
