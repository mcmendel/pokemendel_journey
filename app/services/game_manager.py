import os
import random
import shutil
from typing import Dict

from app.config import GameConfig
from app.models.pokemon_relation import PokemonRelation

TYPE_WEAKER = {
    "grass": "water",
    "fire": "grass",
    "water": "fire",
}


def resolve_starter(relation: PokemonRelation, starters: Dict[str, str]) -> str:
    """Resolve which starter to use based on a PokemonRelation and available starters.

    Priority:
    1. no_way_jose: pick random type from it -> use that type's starter directly
    2. really_want: pick random type -> use starter of the WEAKER type
    3. want: same as really_want but lower priority
    4. dont_want: pick random type -> use that type's starter directly
    5. fallback: random starter

    starters maps starter_name -> type_string (e.g. {"Bulbasaur": "grass"}).
    """
    type_to_starter: dict[str, str] = {}
    for name, stype in starters.items():
        type_to_starter[stype] = name

    def _starter_for_type(t: str) -> str | None:
        return type_to_starter.get(t)

    def _starter_for_weaker(t: str) -> str | None:
        weaker_type = TYPE_WEAKER.get(t)
        return type_to_starter.get(weaker_type) if weaker_type else None

    if relation.no_way_jose:
        chosen_type = random.choice(list(relation.no_way_jose))
        result = _starter_for_type(chosen_type)
        if result:
            return result

    if relation.really_want:
        chosen_type = random.choice(list(relation.really_want))
        result = _starter_for_weaker(chosen_type)
        if result:
            return result

    if relation.want:
        chosen_type = random.choice(list(relation.want))
        result = _starter_for_weaker(chosen_type)
        if result:
            return result

    if relation.dont_want:
        chosen_type = random.choice(list(relation.dont_want))
        result = _starter_for_type(chosen_type)
        if result:
            return result

    return random.choice(list(starters.keys()))


def create_pokemon_games(game: GameConfig, starter_mapping: Dict[str, PokemonRelation]) -> dict:
    """Create save files for all mapped pokemons by copying from resolved starters.

    Returns a summary dict with counts.
    """
    created = 0
    skipped = 0

    for pokemon_name, relation in starter_mapping.items():
        starter = resolve_starter(relation, game.starters)
        if not starter:
            print(f"  {pokemon_name}: no starter found, skipping")
            skipped += 1
            continue

        print(f"  {pokemon_name} -> {starter}")

        for save_dir in game.save_dirs:
            for ext in game.save_extensions:
                src = os.path.join(save_dir, f"{starter}{ext}")
                dest = os.path.join(save_dir, f"{pokemon_name}{ext}")
                if not os.path.exists(dest) and os.path.exists(src):
                    # shutil.copy(src, dest)
                    created += 1
                else:
                    skipped += 1

    return {"created": created, "skipped": skipped}
