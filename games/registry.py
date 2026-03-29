from typing import Dict

from app.models.pokemon_relation import PokemonRelation


def get_starter_mapping(game_id: str) -> Dict[str, PokemonRelation]:
    if game_id == "blue":
        from games.gen1.blue.starter_mapping import STARTER_MAPPING
        return STARTER_MAPPING

    if game_id == "crystal":
        from games.gen2.starter_mappings import STARTER_MAPPING
        return STARTER_MAPPING

    if game_id == "emerald":
        from games.gen3.starter_mappings import STARTER_MAPPING
        return STARTER_MAPPING

    if game_id == "platinum":
        from games.gen4.starter_mappings import STARTER_MAPPING
        return STARTER_MAPPING

    raise ValueError(f"No starter mapping for game: {game_id}")
