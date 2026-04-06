from flask import Blueprint, render_template, current_app, abort, jsonify

from app.services.game_manager import create_pokemon_games, get_current_pokemon, navigate_pokemon, get_cheat_codes
from app.services.pokemon_service import get_marked_pokemon_entries, is_eevee_family, get_pokemon_stats
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


def _get_sorted_entries(generation: int) -> list:
    return get_marked_pokemon_entries(generation)


def _entry_to_dict(entry, generation: int) -> dict:
    d = {
        "name": entry.name,
        "base": entry.base,
        "evolution_details": entry.evolution_details,
    }
    stats = get_pokemon_stats(entry.name, generation)
    if stats:
        d["stats"] = stats
    return d


@pokemon_bp.route("/game/<game_id>/replace")
def replace_page(game_id):
    games = current_app.config["GAMES"]
    game = games.get(game_id)
    if not game:
        abort(404)

    entries = _get_sorted_entries(game.generation)
    pokemon_names = [e.name for e in entries]
    current = get_current_pokemon(game_id, pokemon_names)
    if current["name"]:
        entry = entries[current["index"]]
        current["base"] = entry.base
        current["evolution_details"] = entry.evolution_details
        current["stats"] = get_pokemon_stats(current["name"], game.generation, base=entry.base)
    else:
        current["base"] = None
        current["evolution_details"] = ""
        current["stats"] = None

    image_base_url = current_app.config["POKEMON_IMAGE_BASE_URL"]
    return render_template("replace.html", games=games, game=game, game_id=game_id, current=current, image_base_url=image_base_url)


@pokemon_bp.route("/api/game/<game_id>/navigate", methods=["POST"])
def navigate(game_id):
    games = current_app.config["GAMES"]
    game = games.get(game_id)
    if not game:
        abort(404)

    from flask import request
    direction = request.json.get("direction", "next")
    if direction not in ("next", "prev"):
        return jsonify({"error": "direction must be 'next' or 'prev'"}), 400

    entries = _get_sorted_entries(game.generation)
    pokemon_names = [e.name for e in entries]
    result = navigate_pokemon(game_id, game, pokemon_names, direction)

    entry = entries[result["index"]]
    result["base"] = entry.base
    result["evolution_details"] = entry.evolution_details
    result["stats"] = get_pokemon_stats(result["name"], game.generation, base=entry.base)
    cheat_pokemon = result["name"] if is_eevee_family(entry.name, entry.base) else entry.base
    result["cheat_codes"] = get_cheat_codes(game, cheat_pokemon)
    return jsonify(result)
