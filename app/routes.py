from flask import Blueprint

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

@bp.route("/login")
def login():
    return "Login Page", 200

