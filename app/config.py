import os
from dataclasses import dataclass, field
from typing import Dict, List

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


@dataclass
class GameConfig:
    generation: int
    display_name: str
    rom_extension: str
    base_rom_path: str
    pokemon_dir: str
    save_dirs: List[str] = field(default_factory=list)
    save_extensions: List[str] = field(default_factory=list)
    starters: Dict[str, str] = field(default_factory=dict)


@dataclass
class AppConfig:
    games: Dict[str, GameConfig]
    pokemon_image_base_url: str = ""


def load_config() -> AppConfig:
    with open(CONFIG_PATH, "r") as f:
        raw = yaml.safe_load(f)

    games = {}
    for game_id, game_data in raw.get("games", {}).items():
        games[game_id] = GameConfig(**game_data)

    return AppConfig(
        games=games,
        pokemon_image_base_url=raw.get("pokemon_image_base_url", ""),
    )
