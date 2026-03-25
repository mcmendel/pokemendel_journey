from flask import Blueprint, render_template, current_app

pokemon_bp = Blueprint("pokemon", __name__)


@pokemon_bp.route("/")
def index():
    games = current_app.config["GAMES"]
    return render_template("index.html", games=games)
