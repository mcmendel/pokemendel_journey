from flask import Blueprint, render_template, current_app, abort

from app.services.pokemon_service import get_marked_pokemon_entries

pokemon_bp = Blueprint("pokemon", __name__)


@pokemon_bp.route("/")
def index():
    games = current_app.config["GAMES"]
    return render_template("index.html", games=games)


@pokemon_bp.route("/game/<game_id>/")
def game_page(game_id):
    games = current_app.config["GAMES"]
    game = games.get(game_id)
    if not game:
        abort(404)

    pokemons = get_marked_pokemon_entries(game.generation)
    return render_template("game.html", games=games, game=game, game_id=game_id, pokemons=pokemons)
