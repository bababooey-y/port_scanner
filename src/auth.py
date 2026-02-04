from flask import request, render_template, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from src.db import USERS

auth_blueprint = Blueprint("auth",__name__)


@auth_blueprint.get("/register")
def get_register():
    return render_template("register.html")

@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")
    secure_password = generate_password_hash(password)
    if username not in USERS.keys():
        USERS[username] = secure_password
        return redirect(url_for("auth.get_login"))

    print("utilisateur non ajouté")
    return redirect(url_for("auth.get_login"))

@auth_blueprint.get("/login")
def get_login():
    return render_templates("login.html")

@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username")
    password_hash = form.get("password")



