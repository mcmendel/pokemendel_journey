from dataclasses import dataclass, field


@dataclass
class PokemonRelation:
    really_want: set[str] = field(default_factory=set)
    want: set[str] = field(default_factory=set)
    dont_want: set[str] = field(default_factory=set)
    no_way_jose: set[str] = field(default_factory=set)
