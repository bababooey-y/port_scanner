from flask import request, render_template, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash

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
    print(username, password, secure_password)
    return