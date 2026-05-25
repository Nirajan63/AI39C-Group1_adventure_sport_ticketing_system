from flask import Blueprint, request, jsonify, session
from app.models.user import users_db, bookings_db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


# ── Login ─────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing request body', 'status': 'error'}), 400

    username = data.get('username')
    password = data.get('password')

    user = next((u for u in users_db if u['username'] == username and u['password'] == password), None)

    if user:
        return jsonify({
            'message': 'Login successful',
            'status': 'success',
            'user': {'username': user['username'], 'email': user['email']}
        }), 200
    else:
        return jsonify({'message': 'Invalid credentials', 'status': 'error'}), 401


# ── Signup ────────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing request body', 'status': 'error'}), 400

    username = data.get('username')
    email    = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'All fields are required', 'status': 'error'}), 400

    if any(u['username'] == username for u in users_db):
        return jsonify({'message': 'Username already exists', 'status': 'error'}), 400

    users_db.append({'username': username, 'email': email, 'password': password})
    bookings_db[username] = []

    return jsonify({'message': 'User registered successfully', 'status': 'success'}), 201


# ── Reset Password ────────────────────────────────────────────────
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing request body', 'status': 'error'}), 400

    new_password = data.get('password')
    if not new_password:
        return jsonify({'message': 'New password is required', 'status': 'error'}), 400

    for u in users_db:
        if u['username'] == 'testuser':
            u['password'] = new_password

    return jsonify({'message': 'Password reset successful', 'status': 'success'}), 200


# ── Dashboard — user profile + stats ─────────────────────────────
@auth_bp.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.json or {}
    username = data.get('username')

    if not username:
        return jsonify({'message': 'Username required', 'status': 'error'}), 400

    user = next((u for u in users_db if u['username'] == username), None)
    if not user:
        return jsonify({'message': 'User not found', 'status': 'error'}), 404

    user_bookings = bookings_db.get(username, [])

    total_spent    = sum(b['total'] for b in user_bookings)
    completed      = [b for b in user_bookings if b['status'] == 'completed']
    upcoming       = [b for b in user_bookings if b['status'] == 'confirmed']
    activities_set = list({b['activity'] for b in user_bookings})

    return jsonify({
        'status': 'success',
        'user': {
            'username': user['username'],
            'email':    user['email'],
            'joined':   'May 2026'
        },
        'stats': {
            'total_bookings':    len(user_bookings),
            'completed':         len(completed),
            'upcoming':          len(upcoming),
            'total_spent':       total_spent,
            'unique_activities': len(activities_set)
        },
        'bookings': user_bookings
    }), 200


# ── Add Booking ───────────────────────────────────────────────────
@auth_bp.route('/book', methods=['POST'])
def book():
    data = request.json or {}
    username    = data.get('username')
    activity_id = data.get('activity_id')
    date        = data.get('date')
    people      = int(data.get('people', 1))

    ACTIVITIES = {
        'paragliding': {'name': 'Paragliding',          'emoji': '🪂', 'price': 4500, 'location': 'Pokhara',          'difficulty': 'Moderate',    'duration': '30 min'},
        'bungee':      {'name': 'Bungee Jumping',        'emoji': '🤸', 'price': 6000, 'location': 'The Last Resort',  'difficulty': 'Extreme',     'duration': '2 hrs'},
        'rafting':     {'name': 'White-Water Rafting',   'emoji': '🚣', 'price': 3200, 'location': 'Trishuli River',   'difficulty': 'Challenging', 'duration': 'Full day'},
        'trekking':    {'name': 'Himalayan Trekking',    'emoji': '🏔️', 'price': 8500, 'location': 'Annapurna Region','difficulty': 'Varies',      'duration': '3–7 days'},
        'zipline':     {'name': 'Zip-lining',            'emoji': '⚡', 'price': 3800, 'location': 'Pokhara',          'difficulty': 'Moderate',    'duration': '1 hr'},
        'canyoning':   {'name': 'Canyoning',             'emoji': '🌊', 'price': 4200, 'location': 'Jalbire',          'difficulty': 'Challenging', 'duration': 'Half day'},
    }

    if not username or activity_id not in ACTIVITIES:
        return jsonify({'message': 'Invalid booking data', 'status': 'error'}), 400

    act = ACTIVITIES[activity_id]
    booking_id = f"TS{datetime.now().strftime('%H%M%S')}"

    booking = {
        'id':         booking_id,
        'activity':   act['name'],
        'emoji':      act['emoji'],
        'location':   act['location'],
        'date':       date,
        'people':     people,
        'price':      act['price'],
        'total':      act['price'] * people,
        'difficulty': act['difficulty'],
        'duration':   act['duration'],
        'status':     'confirmed'
    }

    bookings_db.setdefault(username, []).append(booking)
    return jsonify({'message': 'Booking confirmed!', 'status': 'success', 'booking': booking}), 201
