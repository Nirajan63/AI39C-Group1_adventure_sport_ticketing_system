from flask import render_template, request


class AuthController:
    def login(self):
        if request.method == "POST":
            print(request.form)
        return render_template("login.html")

    def manage(self):
        if request.method == "POST":
            print(request.form)
        return render_template("manage_profile.html")
