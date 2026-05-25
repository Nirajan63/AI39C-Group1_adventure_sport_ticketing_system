# In-Memory Database Simulation

users_db = [
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
]

# In-memory bookings store: { username: [booking, ...] }
bookings_db = {
    "testuser": [
        {
            "id": "TS001",
            "activity": "Paragliding",
            "emoji": "🪂",
            "location": "Pokhara",
            "date": "2026-06-10",
            "people": 2,
            "price": 4500,
            "total": 9000,
            "difficulty": "Moderate",
            "duration": "30 min",
            "status": "confirmed"
        },
        {
            "id": "TS002",
            "activity": "Bungee Jumping",
            "emoji": "🤸",
            "location": "The Last Resort",
            "date": "2026-07-04",
            "people": 1,
            "price": 6000,
            "total": 6000,
            "difficulty": "Extreme",
            "duration": "2 hrs",
            "status": "confirmed"
        },
        {
            "id": "TS003",
            "activity": "White-Water Rafting",
            "emoji": "🚣",
            "location": "Trishuli River",
            "date": "2026-05-20",
            "people": 4,
            "price": 3200,
            "total": 12800,
            "difficulty": "Challenging",
            "duration": "Full day",
            "status": "completed"
        }
    ]
}
