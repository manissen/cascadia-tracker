from datetime import date

import typer
import csv
import json

from rich.console import Console
from rich.table import Table

from cascadia_tracker.storage import load_games, save_games

app = typer.Typer()
console = Console()

def clean_name(name: str) -> str:
    """Standardize player names."""
    return " ".join(name.strip().split()).title()

def calculate_habitat_bonuses(player_results: dict) -> None:
    """Add habitat majority bonuses to each player's result."""

    habitats = ["mountain", "forest", "prairie", "wetland", "river"]
    num_players = len(player_results)

    for player in player_results:
        player_results[player]["habitat_bonus"] = 0

    for habitat in habitats:
        scores = {
            player: result["habitats"][habitat]
            for player, result in player_results.items()
        }

        max_score = max(scores.values())
        first_place_players = [
            player for player, score in scores.items() if score == max_score
        ]

        if num_players == 2:
            if len(first_place_players) == 1:
                player_results[first_place_players[0]]["habitat_bonus"] += 2
            else:
                for player in first_place_players:
                    player_results[player]["habitat_bonus"] += 1
            continue

        if len(first_place_players) == 1:
            first_player = first_place_players[0]
            player_results[first_player]["habitat_bonus"] += 3

            remaining_scores = [
                score for player, score in scores.items() if player != first_player
            ]
            second_score = max(remaining_scores)
            second_place_players = [
                player
                for player, score in scores.items()
                if player != first_player and score == second_score
            ]

            if len(second_place_players) == 1:
                player_results[second_place_players[0]]["habitat_bonus"] += 1

        elif len(first_place_players) == 2:
            for player in first_place_players:
                player_results[player]["habitat_bonus"] += 2

        else:
            for player in first_place_players:
                player_results[player]["habitat_bonus"] += 1


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
    player_results = {}

    for player in players:
        typer.echo(f"\nScores for {player}")

        bear = typer.prompt("Bear score", type=int)
        elk = typer.prompt("Elk score", type=int)
        salmon = typer.prompt("Salmon score", type=int)
        hawk = typer.prompt("Hawk score", type=int)
        fox = typer.prompt("Fox score", type=int)
        habitats = {
            "mountain": typer.prompt("Mountain corridor score", type=int),
            "forest": typer.prompt("Forest corridor score", type=int),
            "prairie": typer.prompt("Prairie corridor score", type=int),
            "wetland": typer.prompt("Wetland corridor score", type=int),
            "river": typer.prompt("River corridor score", type=int),
        }

        nature_tokens = typer.prompt("Nature token score", type=int)

        landmark_scores = {
            "habitat": {},
            "end_game": {},
        }

        if used_landmarks:
            habitat_landmarks_input = typer.prompt(
                f"Habitat-scored landmarks for {player}, like River-G, Prairie-A",
                default="",
            )
            habitat_landmarks = [
                landmark.strip()
                for landmark in habitat_landmarks_input.split(",")
                if landmark.strip()
            ]

            for landmark in habitat_landmarks:
                landmark_scores["habitat"][landmark] = typer.prompt(
                    f"{player}'s {landmark} score during habitat scoring",
                    type=int,
                )

            end_game_landmarks_input = typer.prompt(
                f"End-game landmarks for {player}, like Mountain-C",
                default="",
            )
            end_game_landmarks = [
                landmark.strip()
                for landmark in end_game_landmarks_input.split(",")
                if landmark.strip()
            ]

            for landmark in end_game_landmarks:
                landmark_scores["end_game"][landmark] = typer.prompt(
                    f"{player}'s {landmark} end-game score",
                    type=int,
                )
        total = (
            bear
            + elk
            + salmon
            + hawk
            + fox
            + sum(habitats.values())
            + nature_tokens
            + sum(landmark_scores["habitat"].values())
            + sum(landmark_scores["end_game"].values())
        )

        player_results[player] = {
            "bear": bear,
            "elk": elk,
            "salmon": salmon,
            "hawk": hawk,
            "fox": fox,
            "habitats": habitats,
            "habitat_bonus": 0,
            "nature_tokens": nature_tokens,
            "landmarks": landmark_scores,
            "total": total,
        }

        typer.echo(f"Total for {player}: {total}")
    
    calculate_habitat_bonuses(player_results)

    for result in player_results.values():
        result["total"] += result["habitat_bonus"]

    winner = max(player_results, key=lambda p: player_results[p]["total"])

    notes = typer.prompt("Notes", default="")

    game = {
        "date": game_date,
        "players": players,
        "scoring_cards": scoring_cards,
        "used_landmarks": used_landmarks,
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

        for result in game["results"].values():
            for score_type in ["habitat", "end_game"]:
                for landmark, score in result["landmarks"][score_type].items():
                    key = f"{landmark} ({score_type})"

                    landmark_counts[key] = landmark_counts.get(key, 0) + 1
                    landmark_scores.setdefault(key, [])
                    landmark_scores[key].append(score)

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
    
@app.command()
def category_stats():
    """Show each player's average score by category."""

    games = load_games()
    categories = [
        "bear",
        "elk",
        "salmon",
        "hawk",
        "fox",
        "nature_tokens",
    ]

    player_scores = {}

    for game in games:
        for player, result in game["results"].items():
            player_scores.setdefault(player, {category: [] for category in categories})

            for category in categories:
                player_scores[player][category].append(result[category])

    if not player_scores:
        typer.echo("No games logged yet.")
        return

    typer.echo("\nCategory Leaders")
    typer.echo("----------------")

    for category in categories:
        best_player = None
        best_average = -1

        for player, scores_by_category in player_scores.items():
            scores = scores_by_category[category]
            average = sum(scores) / len(scores)

            if average > best_average:
                best_average = average
                best_player = player

        typer.echo(
            f"{category.replace('_', ' ').title()}: "
            f"{best_player} with avg {best_average:.2f}"
        )

@app.command()
def best_games(limit: int = 10):
    """Show the best individual scores ever."""

    games = load_games()
    rows = []

    for game in games:
        for player, result in game["results"].items():
            rows.append((result["total"], player, game["date"]))

    if not rows:
        typer.echo("No games logged yet.")
        return

    rows.sort(reverse=True)

    table = Table(title="Best Cascadia Games")
    table.add_column("Rank")
    table.add_column("Player")
    table.add_column("Score")
    table.add_column("Date")

    for rank, (score, player, game_date) in enumerate(rows[:limit], start=1):
        table.add_row(str(rank), player, str(score), game_date)

    console.print(table)

@app.command()
def rivalry(player_one: str, player_two: str):
    """Show head-to-head stats for two players."""

    player_one = clean_name(player_one)
    player_two = clean_name(player_two)

    games = load_games()

    games_together = 0
    player_one_wins = 0
    player_two_wins = 0
    margins = []

    for game in games:
        results = game["results"]

        if player_one in results and player_two in results:
            games_together += 1

            score_one = results[player_one]["total"]
            score_two = results[player_two]["total"]
            margins.append(abs(score_one - score_two))

            if score_one > score_two:
                player_one_wins += 1
            elif score_two > score_one:
                player_two_wins += 1

    if games_together == 0:
        typer.echo(f"No games found with both {player_one} and {player_two}.")
        return

    avg_margin = sum(margins) / len(margins)

    table = Table(title=f"{player_one} vs {player_two}")
    table.add_column("Stat")
    table.add_column("Value")

    table.add_row("Games together", str(games_together))
    table.add_row(f"{player_one} wins", str(player_one_wins))
    table.add_row(f"{player_two} wins", str(player_two_wins))
    table.add_row("Average margin", f"{avg_margin:.2f}")

    console.print(table)

@app.command()
def export_csv(filename: str = "cascadia_games.csv"):
    """Export logged games to a CSV file."""

    games = load_games()

    if not games:
        typer.echo("No games logged yet.")
        return

    fieldnames = [
        "date",
        "player",
        "total",
        "winner",
        "bear",
        "elk",
        "salmon",
        "hawk",
        "fox",
        "mountain",
        "forest",
        "prairie",
        "wetland",
        "river",
        "habitat_bonus",
        "nature_tokens",
        "used_landmarks",
        "habitat_landmarks",
        "habitat_landmark_score",
        "end_game_landmarks",
        "end_game_landmark_score",
        "all_landmarks",
        "notes",
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for game in games:
            for player, result in game["results"].items():
                habitat_landmarks = result["landmarks"]["habitat"]
                end_game_landmarks = result["landmarks"]["end_game"]

                all_landmarks = {
                    "habitat": habitat_landmarks,
                    "end_game": end_game_landmarks,
                }

                writer.writerow(
                    {
                        "date": game["date"],
                        "player": player,
                        "total": result["total"],
                        "winner": game["winner"] == player,
                        "bear": result["bear"],
                        "elk": result["elk"],
                        "salmon": result["salmon"],
                        "hawk": result["hawk"],
                        "fox": result["fox"],
                        "mountain": result["habitats"]["mountain"],
                        "forest": result["habitats"]["forest"],
                        "prairie": result["habitats"]["prairie"],
                        "wetland": result["habitats"]["wetland"],
                        "river": result["habitats"]["river"],
                        "habitat_bonus": result["habitat_bonus"],
                        "nature_tokens": result["nature_tokens"],
                        "used_landmarks": game["used_landmarks"],
                        "habitat_landmarks": json.dumps(habitat_landmarks),
                        "habitat_landmark_score": sum(habitat_landmarks.values()),
                        "end_game_landmarks": json.dumps(end_game_landmarks),
                        "end_game_landmark_score": sum(end_game_landmarks.values()),
                        "all_landmarks": json.dumps(all_landmarks),
                        "notes": game["notes"],
                    }
                )

    typer.echo(f"Exported games to {filename}")