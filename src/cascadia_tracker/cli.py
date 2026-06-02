from datetime import date

import typer

from cascadia_tracker.storage import load_games, save_games

app = typer.Typer()


@app.command()
def hello():
    print("Welcome to Cascadia Tracker!")


@app.command()
def add_game():
    """Add a completed Cascadia game with detailed scoring."""

    game_date = typer.prompt("Date", default=str(date.today()))
    players = typer.prompt("Players (comma separated)").split(",")
    players = [p.strip() for p in players]

    scoring_cards = {
        "bear": typer.prompt("Bear scoring card"),
        "elk": typer.prompt("Elk scoring card"),
        "salmon": typer.prompt("Salmon scoring card"),
        "hawk": typer.prompt("Hawk scoring card"),
        "fox": typer.prompt("Fox scoring card"),
    }

    used_landmarks = typer.confirm("Did you use the landmark expansion?")
    landmarks = []

    if used_landmarks:
        landmarks_input = typer.prompt(
            "Landmarks used, like River-G, Prairie-A, Mountain-C"
        )
        landmarks = [
            landmark.strip()
            for landmark in landmarks_input.split(",")
            if landmark.strip()
         ]
    player_results = {}

    for player in players:
        typer.echo(f"\nScores for {player}")

        bear = typer.prompt("Bear score", type=int)
        elk = typer.prompt("Elk score", type=int)
        salmon = typer.prompt("Salmon score", type=int)
        hawk = typer.prompt("Hawk score", type=int)
        fox = typer.prompt("Fox score", type=int)
        habitat = typer.prompt("Habitat score", type=int)
        nature_tokens = typer.prompt("Nature token score", type=int)

        landmark_score = 0
        if used_landmarks:
            landmark_score = typer.prompt("Landmark score", type=int)

        total = (
            bear
            + elk
            + salmon
            + hawk
            + fox
            + habitat
            + nature_tokens
            + landmark_score
        )

        player_results[player] = {
            "bear": bear,
            "elk": elk,
            "salmon": salmon,
            "hawk": hawk,
            "fox": fox,
            "habitat": habitat,
            "nature_tokens": nature_tokens,
            "landmark": landmark_score,
            "total": total,
        }

        typer.echo(f"Total for {player}: {total}")

    winner = max(player_results, key=lambda p: player_results[p]["total"])

    notes = typer.prompt("Notes", default="")

    game = {
        "date": game_date,
        "players": players,
        "scoring_cards": scoring_cards,
        "used_landmarks": used_landmarks,
        "landmarks": landmarks,
        "results": player_results,
        "winner": winner,
        "notes": notes,
    }

    games = load_games()
    games.append(game)
    save_games(games)

    typer.echo(f"\nGame saved! Winner: {winner}")