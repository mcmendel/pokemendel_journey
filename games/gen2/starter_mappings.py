from app.models.pokemon_relation import PokemonRelation
from pokemendel_core.data.gen2 import PokemonGen2

STARTER_MAPPING: dict[str, PokemonRelation] = {
    # Example:
    # PokemonGen2.PIKACHU: PokemonRelation(want={"fire", "water"}, dont_want={"grass"}),
}
