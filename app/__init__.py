from flask import Flask

from app.config import load_config


def create_app():
    app = Flask(__name__)

    app_config = load_config()
    app.config["GAMES"] = app_config.games
    app.config["POKEMON_IMAGE_BASE_URL"] = app_config.pokemon_image_base_url

    from app.routes.pokemon_routes import pokemon_bp
    app.register_blueprint(pokemon_bp)

    return app
