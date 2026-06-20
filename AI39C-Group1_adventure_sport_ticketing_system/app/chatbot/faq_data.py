# app/chatbot/faq_data.py
"""
Static FAQ knowledge base for the SportAdventure chatbot.

These entries are embedded into FAISS at startup (or first request) and
retrieved by semantic similarity inside the `search_faq` tool. Keep each
entry short and self-contained -- it gets dropped directly into the model's
context as a retrieved chunk.

Edit this list freely; there is no migration needed, the FAISS index is
rebuilt from this file whenever the on-disk index is missing or stale
(see faiss_store.py -> get_vector_store()).
"""

FAQ_ENTRIES = [
    {
        "id": "account-signup",
        "question": "How do I create an account?",
        "answer": (
            "Click Register on the top navigation bar and fill in a username, "
            "email, and password. You can also sign in instantly using the "
            "'Sign in with Google' option on the login page, which verifies "
            "your email with a one-time 6-digit code instead of a password."
        ),
    },
    {
        "id": "account-login-otp",
        "question": "I didn't receive my verification code (OTP). What do I do?",
        "answer": (
            "Verification codes expire after 5 minutes. If it hasn't arrived, "
            "wait a moment and request a new one -- each code can only be used "
            "once. Make sure you're checking the same email address you signed "
            "in with."
        ),
    },
    {
        "id": "account-forgot-password",
        "question": "I forgot my password. How do I reset it?",
        "answer": (
            "Go to the Login page and click 'Forgot password?'. Enter your "
            "registered email to receive a 6-digit verification code, then "
            "enter that code along with your new password to complete the reset."
        ),
    },
    {
        "id": "account-suspended",
        "question": "Why was my account suspended or why can't I log in?",
        "answer": (
            "Accounts can be suspended by an administrator, usually for a "
            "policy or payment issue. If you believe this is a mistake, please "
            "contact our support team directly so an admin can review your "
            "account status."
        ),
    },
    {
        "id": "booking-how-to",
        "question": "How do I book an adventure activity or event?",
        "answer": (
            "Open the activity or event page, choose a date and number of "
            "people, and click Book Now. You'll need to be logged in. Once "
            "submitted, your booking appears immediately on your Dashboard "
            "under 'My Bookings'."
        ),
    },
    {
        "id": "booking-cancel",
        "question": "How do I cancel a booking?",
        "answer": (
            "Go to your Dashboard, find the booking under 'My Bookings', and "
            "click Cancel. Only bookings that are still in 'confirmed' status "
            "can be cancelled -- bookings that are already completed or "
            "cancelled cannot be changed."
        ),
    },
    {
        "id": "booking-status-meaning",
        "question": "What do the booking statuses mean?",
        "answer": (
            "'Confirmed' means your slot is reserved and upcoming. 'Completed' "
            "is automatically applied once the activity date has passed. "
            "'Cancelled' means the booking was cancelled by you or by an "
            "admin and is no longer active."
        ),
    },
    {
        "id": "booking-availability",
        "question": "How do I know if an activity or event still has open slots?",
        "answer": (
            "Each activity/event listing shows live ticket or slot "
            "availability. If a date shows as 'limited', only a few spots "
            "remain; 'sold out' means no more bookings can be made for that "
            "date until cancellations free up space."
        ),
    },
    {
        "id": "payment-methods",
        "question": "What payment methods are accepted?",
        "answer": (
            "We support QR/digital payment and manual payment options. After "
            "choosing a payment method at checkout, your booking is marked "
            "pending until payment is verified, after which it moves to "
            "confirmed."
        ),
    },
    {
        "id": "payment-refund",
        "question": "How do refunds work?",
        "answer": (
            "Refunds are processed by our admin team after a cancellation "
            "request is reviewed. Once approved, the booking's payment status "
            "is updated to 'refunded' and you'll receive a notification "
            "confirming it."
        ),
    },
    {
        "id": "wishlist",
        "question": "How does the wishlist work?",
        "answer": (
            "Click the heart icon on any activity or event card to save it to "
            "your Wishlist. Click it again to remove it. You can view all "
            "saved items anytime from the Wishlist page in the navigation bar."
        ),
    },
    {
        "id": "reviews",
        "question": "Can I leave a review for an activity?",
        "answer": (
            "Yes -- visit the Reviews page and submit your rating (1-5 stars) "
            "and feedback for any activity you've experienced. You can edit or "
            "delete your own reviews at any time from the same page."
        ),
    },
    {
        "id": "gallery",
        "question": "What is the Gallery page?",
        "answer": (
            "The Gallery showcases photos from past adventures shared by our "
            "team, so you can see what an activity looks like before booking."
        ),
    },
    {
        "id": "safety",
        "question": "Are the adventure activities safe and certified?",
        "answer": (
            "All listed activities are run by safety-licensed and certified "
            "operators. Specific safety equipment and guide certifications "
            "vary by activity -- check the individual activity page for "
            "details, or ask our support team."
        ),
    },
    {
        "id": "group-bookings",
        "question": "Can I book for a group?",
        "answer": (
            "Yes, when booking you can specify the number of people joining "
            "you. The total price scales with the number of participants, "
            "and availability is checked against the remaining capacity for "
            "that date."
        ),
    },
    {
        "id": "contact-support",
        "question": "How do I contact support or report an issue?",
        "answer": (
            "You can use this chat assistant for quick questions, or reach "
            "out through the contact details in the website footer for "
            "issues that need direct human follow-up, such as account or "
            "payment disputes."
        ),
    },
]
