from pokemendel_core.utils.evolutions import (
    MarkedPokemonEntry,
    get_marked_pokemon_entries,
    is_eevee_family,
)

_NAME_TO_POKEMON_BY_GEN = {}


def _get_name_to_pokemon(generation: int) -> dict:
    if generation not in _NAME_TO_POKEMON_BY_GEN:
        mod = __import__(f"pokemendel_core.data.gen{generation}", fromlist=["NAME_TO_POKEMON"])
        _NAME_TO_POKEMON_BY_GEN[generation] = mod.NAME_TO_POKEMON
    return _NAME_TO_POKEMON_BY_GEN[generation]


def _get_final_evolution(name: str, lookup: dict) -> str:
    """Follow the evolution chain to its end, taking the first branch at splits."""
    visited = {name}
    current = name
    while True:
        pokemon = lookup.get(current)
        if not pokemon or not pokemon.evolves_to:
            return current
        next_name = pokemon.evolves_to[0].name
        if next_name in visited or next_name not in lookup:
            return current
        visited.add(next_name)
        current = next_name


def get_pokemon_stats(name: str, generation: int, base: str | None = None) -> dict | None:
    """Return final evolution's attack and special_attack, plus its name.

    Eevee family members show their own stats instead of following the chain.
    """
    lookup = _get_name_to_pokemon(generation)
    if is_eevee_family(name, base or name):
        final = name
    else:
        final = _get_final_evolution(name, lookup)
    pokemon = lookup.get(final)
    if pokemon and pokemon.stats:
        result = {"attack": pokemon.stats.attack, "special_attack": pokemon.stats.special_attack}
        if final != name:
            result["final_evo"] = final
        return result
    return None


def get_image_slug(name: str, generation: int) -> str:
    """Return the image filename slug matching download_pokemon_from_google_search output.

    For form Pokemon (e.g. Heat Rotom) the slug is "{base_name}-{form}" (e.g. "Rotom-Heat").
    For regular Pokemon the slug is the Pokemon's name.
    """
    lookup = _get_name_to_pokemon(generation)
    pokemon = lookup.get(name)
    if pokemon and pokemon.form and pokemon.base_name:
        return f"{pokemon.base_name}-{pokemon.form}"
    return name


__all__ = ["MarkedPokemonEntry", "get_marked_pokemon_entries", "is_eevee_family", "get_pokemon_stats", "get_image_slug"]
