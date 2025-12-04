from flask import Flask

from src.forms import forms_blueprint
from src.auth import auth_blueprint



def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "clef"
    app.register_blueprint(forms_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
