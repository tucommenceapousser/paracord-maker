from flask import Flask, render_template, request, flash
from markupsafe import escape
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_talisman import Talisman
import json

# Initialisation Flask
app = Flask(__name__)
app.secret_key = 'Trh@ckn0n'  # À remplacer par une vraie clé secrète en prod
Talisman(app)

# Sécurité des cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Chargement de la base de données des tressages
with open("data/braids.json", "r", encoding="utf-8") as f:
    BRAID_DB = json.load(f)

# Formulaire sécurisé avec Flask-WTF
class BraidForm(FlaskForm):
    wrist = FloatField("Longueur du tressage apres deduction de la boucle (cm)", validators=[DataRequired(), NumberRange(min=10, max=30)])
    knot = SelectField("Type de tressage", validators=[DataRequired()])
    cord_count = IntegerField("Nombre de cordes", validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField("Calculer")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.knot.choices = [(b["name"], b["name"]) for b in BRAID_DB]
# Fonction de calcul de longueur

def calc_paracord(wrist_cm, braid_name, num_cords):
    braid = next((b for b in BRAID_DB if b["name"] == braid_name), None)
    if not braid:
        return []
    base = braid["cord_per_cm"]
    total_length = (wrist_cm + 3) * base
    length_per_cord = total_length / num_cords
    return [round(length_per_cord, 2) for _ in range(num_cords)]

# Route principale sécurisée
@app.route("/", methods=["GET", "POST"])
def index():
    form = BraidForm()
    results = []
    if form.validate_on_submit():
        wrist = form.wrist.data
        knot = form.knot.data
        cord_count = form.cord_count.data
        results = calc_paracord(wrist, knot, cord_count)
    elif request.method == "POST":
        flash("Veuillez corriger les erreurs dans le formulaire", "danger")
    return render_template("index.html", form=form, results=results, braids=BRAID_DB)

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")
