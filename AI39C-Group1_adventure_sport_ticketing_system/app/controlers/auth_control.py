from flask import render_template, request, jsonify
import sqlite3
import random
import time
from app.models.database import get_db_connection
from app.utils.email import send_email


otp_store = {}

class AuthController:
    def login(self):
        if request.method == "POST":
            print(request.form)
        return render_template("login.html")

    def manage(self):
        if request.method == "POST":
            print(request.form)
        return render_template("manage_profile.html")

    def register_page(self):
        return render_template("register.html")

    @staticmethod
    def signup():
        data = request.json
        if not data:
            return jsonify({'message': 'Missing request body', 'status': 'error'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'message': 'All fields are required', 'status': 'error'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        cursor.execute('SELECT * FROM users WHERE username = ? COLLATE NOCASE', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Username already exists', 'status': 'error'}), 400
            
        
        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'message': 'Username already exists', 'status': 'error'}), 400
        
        conn.close()
        return jsonify({'message': 'User registered successfully', 'status': 'success'}), 201
  



    @staticmethod
    def google_send_otp():
        data = request.json
        if not data:
            return jsonify({'message': 'Missing request body', 'status': 'error'}), 400
            
        email = data.get('email')
        if not email:
            return jsonify({'message': 'Email is required', 'status': 'error'}), 400

        
        otp_code = f"{random.randint(100000, 999999)}"
        
        
        try:
            import os
            mock_otp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mock_otp.txt')
            with open(mock_otp_path, 'w') as f:
                f.write(otp_code)
        except Exception as e:
            print(f"Error writing mock OTP file: {e}", flush=True)
        
        
        otp_store[email] = {
            'code': otp_code,
            'expires_at': time.time() + 300
        }

        
        subject = "SportAdventure Google Sign-in Verification Code"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #0b57d0; text-align: center;">Google Sign-In Verification</h2>
                <p>Hello,</p>
                <p>You have selected <strong>{email}</strong> to sign in to SportAdventure via Google. Please use the following 6-digit verification code to complete the login:</p>
                <div style="background-color: #f1f5fb; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #0b57d0; border-radius: 5px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="font-size: 12px; color: #777;">This code is valid for 5 minutes. If you did not request this, you can safely ignore this email.</p>
                <br>
                <p>Best regards,<br>The SportAdventure Team</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Your SportAdventure Google Sign-in Verification Code is: {otp_code}. Valid for 5 minutes."

        success = send_email(email, subject, html_content, text_content)
        if success:
            return jsonify({'message': 'Verification code sent successfully', 'status': 'success'}), 200
        else:
            return jsonify({'message': 'Failed to send verification code', 'status': 'error'}), 500

    @staticmethod
    def google_verify_otp():
        data = request.json
        if not data:
            return jsonify({'message': 'Missing request body', 'status': 'error'}), 400
            
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return jsonify({'message': 'Email and verification code are required', 'status': 'error'}), 400

        
        record = otp_store.get(email)
        if not record:
            return jsonify({'message': 'No verification code was sent to this email', 'status': 'error'}), 400
            
        if time.time() > record['expires_at']:
            
            otp_store.pop(email, None)
            return jsonify({'message': 'Verification code has expired. Please request a new one.', 'status': 'error'}), 400

        if record['code'] != str(code).strip():
            return jsonify({'message': 'Invalid verification code', 'status': 'error'}), 400

        
        otp_store.pop(email, None)

        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ? COLLATE NOCASE', (email,))
        user = cursor.fetchone()
        
        if not user:
            
            username = email.split('@')[0]
            
            base_username = username
            counter = 1
            while True:
                cursor.execute('SELECT * FROM users WHERE username = ? COLLATE NOCASE', (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
                
            
            random_password = f"google_{random.randint(10000000, 99999999)}"
            
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, random_password))
            conn.commit()
            
            
            cursor.execute('SELECT * FROM users WHERE email = ? COLLATE NOCASE', (email,))
            user = cursor.fetchone()
            
        conn.close()

        
        subject = "SportAdventure Connected Successfully!"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #34a853; text-align: center;">Account Successfully Connected!</h2>
                <p>Hello {user['username']},</p>
                <p>We are excited to let you know that your Google Account (<strong>{email}</strong>) has been successfully connected to SportAdventure.</p>
                <p>You can now use this email to quickly sign in to your dashboard anytime.</p>
                <br>
                <p>Best regards,<br>The SportAdventure Team</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Hello {user['username']}, your Google Account ({email}) has been successfully connected to SportAdventure!"
        
        send_email(email, subject, html_content, text_content)

        return jsonify({
            'message': 'Successfully connected',
            'status': 'success',
            'user': {
                'username': user['username'],
                'email': user['email']
            }
        }), 200


