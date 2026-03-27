from app.models.pokemon_relation import PokemonRelation
from pokemendel_core.data.gen3 import PokemonGen3

STARTER_MAPPING: dict[str, PokemonRelation] = {
    # Example:
    # PokemonGen3.PIKACHU: PokemonRelation(want={"fire", "water"}, dont_want={"grass"}),
}
