import json
from pathlib import Path

DATA_DIR = Path.home() / ".cascadia_tracker"
DATA_FILE = DATA_DIR / "games.json"


def load_games():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_games(games):
    DATA_DIR.mkdir(exist_ok=True)

    with open(DATA_FILE, "w") as f:
        json.dump(games, f, indent=2)
