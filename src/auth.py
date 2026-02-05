from flask import request, redirect, url_for, render_template, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash

from src.services.users import create_user, get_user, user_exists

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def get_register():
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")

    if not username or not password:
        return redirect(url_for("auth.get_register"))

    if user_exists(username):
        print("utilisateur déjà existant")
        return redirect(url_for("auth.get_register"))

    password_hash = generate_password_hash(password)
    create_user(username, password_hash)

    return redirect(url_for("auth.get_login"))


@auth_blueprint.get("/login")
def get_login():
    return render_template("login.html")


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")

    user = get_user(username)

    if not user:
        return redirect(url_for("auth.get_login"))

    if check_password_hash(user["password"], password):
        return redirect(url_for("forms.index"))

    return redirect(url_for("auth.get_login"))




