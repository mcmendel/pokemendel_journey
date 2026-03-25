from flask import Blueprint, render_template, current_app, abort, jsonify

from app.services.game_manager import create_pokemon_games
from app.services.pokemon_service import get_marked_pokemon_entries
from games.registry import get_starter_mapping

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


@pokemon_bp.route("/api/game/<game_id>/create", methods=["POST"])
def create_games(game_id):
    games = current_app.config["GAMES"]
    game = games.get(game_id)
    if not game:
        abort(404)

    try:
        starter_mapping = get_starter_mapping(game_id)
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    result = create_pokemon_games(game, starter_mapping)
    return jsonify({
        "message": f"Done! Created {result['created']} files, skipped {result['skipped']}"
    })
