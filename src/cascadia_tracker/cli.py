from datetime import date

import typer

from cascadia_tracker.storage import load_games, save_games

app = typer.Typer()


@app.command()
def hello():
    print("Welcome to Cascadia Tracker!")


@app.command()
def add_game():
    game_date = typer.prompt("Date", default=str(date.today()))

    players = typer.prompt(
        "Players (comma separated)"
    ).split(",")

    players = [p.strip() for p in players]

    scores = {}

    for player in players:
        scores[player] = typer.prompt(
            f"Score for {player}",
            type=int
        )

    game = {
        "date": game_date,
        "players": players,
        "scores": scores,
    }

    games = load_games()
    games.append(game)
    save_games(games)

    print("Game saved!")
