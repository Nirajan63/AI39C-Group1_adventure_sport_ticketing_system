from flask import Blueprint, request

bp = Blueprint("app", __name__)

@bp.route("/")
def home():
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Thrill Sphere</title>
      </head>
      <body>
        <section class="hero">
          <h1>Thrill Sphere</h1>
          <p>Adventure awaits. Explore the world with us.</p>
          <a href="/login">Login</a>
        </section>

        <section id="adventures">
          <h2>Adventures</h2>
          <div class="adventure-list">
            <article>
              <img src="/static/paragliding.jpg" alt="Paragliding">
              <h3>Paragliding</h3>
            </article>
            <article>
              <img src="/static/rafting.jpg" alt="Rafting">
              <h3>Rafting</h3>
            </article>
            <article>
              <img src="/static/trekking.jpg" alt="Trekking">
              <h3>Trekking</h3>
            </article>
          </div>
        </section>

        <section id="contact">
          <h2>Contact Us</h2>
          <p>Visit Our Office for more details.</p>
        </section>
      </body>
    </html>
    """, 200

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            return f"Logged in as {username}", 200
        return "Invalid login", 400

    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Login Page</title>
      </head>
      <body>
        <h1>Login Page</h1>
        <form action="/login" method="post">
          <label for="username">Username</label>
          <input id="username" name="username" type="text" required>

          <label for="password">Password</label>
          <input id="password" name="password" type="password" required>

          <button type="submit">Submit</button>
        </form>

        <p>Don't have an account? <a href="/register">Register here</a>.</p>
      </body>
    </html>
    """, 200

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            return f"Registered {username}", 200
        return "Invalid registration", 400

    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Registration Page</title>
      </head>
      <body>
        <h1>Registration</h1>
        <form action="/register" method="post" class="signup-form">
          <div class="input-box">
            <label for="username">Username</label>
            <input id="username" name="username" type="text" required>
          </div>

          <div class="input-box">
            <label for="email">Email</label>
            <input id="email" name="email" type="email" required>
          </div>

          <div class="input-box">
            <label for="password">Password</label>
            <input id="password" name="password" type="password" required>
          </div>

          <button type="submit">Submit</button>
        </form>

        <p>Already have an account? <a href="/login">Log in here</a>.</p>
      </body>
    </html>
    """, 200

