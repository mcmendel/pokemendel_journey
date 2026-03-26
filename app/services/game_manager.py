import json
import os
import random
import shutil
from typing import Dict, List

from app.config import GameConfig
from app.models.pokemon_relation import PokemonRelation

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

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
                    shutil.copy(src, dest)
                    created += 1
                else:
                    skipped += 1

    return {"created": created, "skipped": skipped}


def _state_path(game_id: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{game_id}_state.json")


def _load_state(game_id: str) -> dict:
    path = _state_path(game_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"index": -1}


def _save_state(game_id: str, state: dict):
    with open(_state_path(game_id), "w") as f:
        json.dump(state, f)


def get_current_pokemon(game_id: str, pokemon_names: List[str]) -> dict:
    state = _load_state(game_id)
    index = state["index"]
    if index < 0 or index >= len(pokemon_names):
        return {"index": -1, "name": None, "total": len(pokemon_names)}
    return {"index": index, "name": pokemon_names[index], "total": len(pokemon_names)}


def navigate_pokemon(game_id: str, game: GameConfig, pokemon_names: List[str], direction: str) -> dict:
    """Move to next or previous pokemon. direction is 'next' or 'prev'.

    Removes the previous pokemon's ROM file and creates the new one.
    """
    state = _load_state(game_id)
    current_index = state["index"]

    if direction == "next":
        new_index = (current_index + 1) % len(pokemon_names)
    else:
        new_index = (current_index - 1) % len(pokemon_names)

    new_pokemon = pokemon_names[new_index]
    new_rom = os.path.join(game.pokemon_dir, f"{new_pokemon}{game.rom_extension}")
    if not os.path.exists(new_rom):
        shutil.copy(game.base_rom_path, new_rom)
        print(f"  [{game_id}] Created ROM: {new_rom}")

    if 0 <= current_index < len(pokemon_names):
        prev_pokemon = pokemon_names[current_index]
        prev_rom = os.path.join(game.pokemon_dir, f"{prev_pokemon}{game.rom_extension}")
        if os.path.exists(prev_rom):
            os.remove(prev_rom)
            print(f"  [{game_id}] Removed ROM: {prev_rom}")

    prev_letter = pokemon_names[current_index][0].lower() if 0 <= current_index < len(pokemon_names) else ""
    new_letter = new_pokemon[0].lower()
    letter_changed = prev_letter != new_letter

    if letter_changed:
        state["letter_count"] = 1
    else:
        state["letter_count"] = state.get("letter_count", 0) + 1

    group_mark = not letter_changed and state["letter_count"] % 4 == 0

    state["index"] = new_index
    _save_state(game_id, state)

    print(f"  [{game_id}] {direction}: index {new_index}, pokemon {new_pokemon}")

    return {
        "index": new_index,
        "name": new_pokemon,
        "total": len(pokemon_names),
        "letter_changed": letter_changed,
        "group_mark": group_mark,
    }
