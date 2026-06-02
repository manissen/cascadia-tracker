from datetime import date

import typer

from cascadia_tracker.storage import load_games, save_games

app = typer.Typer()

def clean_name(name: str) -> str:
    """Standardize player names."""
    return " ".join(name.strip().split()).title()


@app.command()
def hello():
    print("Welcome to Cascadia Tracker!")


@app.command()
def add_game():
    """Add a completed Cascadia game with detailed scoring."""

    game_date = typer.prompt("Date", default=str(date.today()))
    players = typer.prompt("Players (comma separated)").split(",")
    players = [clean_name(p) for p in players if p.strip()]

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

        landmark_scores = {}

        if used_landmarks:
            for landmark in landmarks:
                landmark_scores[landmark] = typer.prompt(
                    f"{landmark} score",
                    type=int,
                )
        total = (
            bear
            + elk
            + salmon
            + hawk
            + fox
            + habitat
            + nature_tokens
            + sum(landmark_scores.values())
        )

        player_results[player] = {
            "bear": bear,
            "elk": elk,
            "salmon": salmon,
            "hawk": hawk,
            "fox": fox,
            "habitat": habitat,
            "nature_tokens": nature_tokens,
            "landmarks": landmark_scores,
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
    
@app.command()
def leaderboard():
    """Show the top Cascadia scores."""

    games = load_games()
    scores = []

    for game in games:
        for player, result in game["results"].items():
            scores.append(
                {
                    "player": player,
                    "score": result["total"],
                    "date": game["date"],
                    "winner": game["winner"] == player,
                }
            )

    if not scores:
        typer.echo("No games logged yet.")
        return

    scores.sort(key=lambda row: row["score"], reverse=True)

    typer.echo("\nTop Scores")
    typer.echo("----------")

    for row in scores[:10]:
        winner_mark = " 🏆" if row["winner"] else ""
        typer.echo(
            f"{row['player']}: {row['score']} points on {row['date']}{winner_mark}"
        )

@app.command()
def player_stats(name: str):
    """Show stats for one player."""
    
    name = clean_name(name)
    games = load_games()

    scores = []
    wins = 0

    for game in games:
        if name in game["results"]:
            result = game["results"][name]
            scores.append(result["total"])

            if game["winner"] == name:
                wins += 1

    if not scores:
        typer.echo(f"No games found for {name}.")
        return

    average_score = sum(scores) / len(scores)
    high_score = max(scores)
    low_score = min(scores)

    typer.echo(f"\nStats for {name}")
    typer.echo("----------------")
    typer.echo(f"Games played: {len(scores)}")
    typer.echo(f"Wins: {wins}")
    typer.echo(f"Win rate: {wins / len(scores):.1%}")
    typer.echo(f"Average score: {average_score:.2f}")
    typer.echo(f"High score: {high_score}")
    typer.echo(f"Low score: {low_score}") 
    
@app.command()
def animal_stats():
    """Show average score for each wildlife category."""

    games = load_games()
    animals = ["bear", "elk", "salmon", "hawk", "fox"]
    totals = {animal: [] for animal in animals}

    for game in games:
        for result in game["results"].values():
            for animal in animals:
                totals[animal].append(result[animal])

    if not games:
        typer.echo("No games logged yet.")
        return

    typer.echo("\nAverage Wildlife Scores")
    typer.echo("-----------------------")

    for animal, scores in totals.items():
        average = sum(scores) / len(scores)
        high = max(scores)
        typer.echo(f"{animal.title()}: avg {average:.2f}, high {high}")

@app.command()
def landmark_stats():
    """Show landmark usage and scoring statistics."""

    games = load_games()
    landmark_counts = {}
    landmark_scores = {}

    for game in games:
        if not game["used_landmarks"]:
            continue

        for landmark in game["landmarks"]:
            landmark_counts[landmark] = landmark_counts.get(landmark, 0) + 1
            landmark_scores.setdefault(landmark, [])

        for result in game["results"].values():
            for landmark, score in result["landmarks"].items():
                landmark_scores.setdefault(landmark, [])
                landmark_scores[landmark].append(score)

    if not landmark_counts:
        typer.echo("No landmark games found.")
        return

    typer.echo("\nLandmark Statistics")
    typer.echo("-------------------")

    for landmark in sorted(landmark_counts, key=landmark_counts.get, reverse=True):
        scores = landmark_scores[landmark]
        avg_score = sum(scores) / len(scores)
        high_score = max(scores)

        typer.echo(
            f"{landmark}: used {landmark_counts[landmark]} game(s), "
            f"avg score {avg_score:.2f}, high score {high_score}"
        )