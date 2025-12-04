from flask import Flask, render_template, redirect, url_for, session, Blueprint, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from src.core.scan import scan
import ipaddress


forms_blueprint = Blueprint("forms", __name__)

#app = Flask(__name__)
#app.config["SECRET_KEY"] = "clef"


class Form(FlaskForm):
    adresse_ip = StringField("Adresse IP: ", validators=[DataRequired()])
    port = StringField("Port(s): ", validators=[DataRequired()])
    submit = SubmitField("Envoyer")

@forms_blueprint.route("/", methods=["GET", "POST"])
def index():
    formulaire = Form()

    if formulaire.validate_on_submit():
        if 1<= int(formulaire.port.data) <= 65535 and ipaddress.ip_address(formulaire.adresse_ip.data):
            session["adresse_ip"] = formulaire.adresse_ip.data
            session["port"] = formulaire.port.data

            return redirect(url_for("forms.scan_form"))
    return render_template("template.html", form = formulaire)


@forms_blueprint.route("/scan")
def scan_form():
    ip_adresse = session.get("adresse_ip")
    ports = session.get('port')
    return render_template('scan.html', adresse_ip = ip_adresse, port = ports)

@forms_blueprint.route("/result")
def result():
    adresse_ip = session.get("adresse_ip")
    port = session.get('port')
    resultat = scan(adresse_ip, int(port))

    return render_template('result.html', result = resultat, ip = adresse_ip, p = port)








