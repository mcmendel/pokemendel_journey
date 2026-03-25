from flask import Flask

from app.config import load_config


def create_app():
    app = Flask(__name__)

    app.config["GAMES"] = load_config()

    from app.routes.pokemon_routes import pokemon_bp
    app.register_blueprint(pokemon_bp)

    return app
