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


def load_config() -> Dict[str, GameConfig]:
    with open(CONFIG_PATH, "r") as f:
        raw = yaml.safe_load(f)

    games = {}
    for game_id, game_data in raw.get("games", {}).items():
        games[game_id] = GameConfig(**game_data)
    return games
