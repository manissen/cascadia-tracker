# Cascadia Tracker

Cascadia Tracker is a command-line tool for logging and analyzing games of **Cascadia** by Randy Flynn. It records detailed information about each game, including player scores, wildlife scoring cards, habitat corridor scores, habitat bonuses, nature tokens, landmark expansion scoring, and notes.

Rather than simply tracking final scores, Cascadia Tracker allows players to analyze long-term trends such as high scores, win rates, category leaders, landmark performance, and head-to-head records between players. Games can also be exported to CSV for additional analysis in Excel, R, or Python.

## Features

- Log completed Cascadia games interactively
- Track the wildlife scoring cards (A–F) used in each game
- Record detailed score breakdowns for every player:
  - Bear
  - Elk
  - Salmon
  - Hawk
  - Fox
  - Habitat corridor scores
  - Automatically calculated habitat bonuses
  - Nature token scores
  - Landmark expansion scores
- View leaderboards and best games
- View player statistics and win rates
- Compare two players head-to-head
- Analyze wildlife scoring categories
- Analyze landmark usage and scoring
- Export all recorded games to CSV

## Installation

Install directly from GitHub using `uv`:

```bash
uv add "git+https://github.com/manissen/cascadia-tracker.git"
```

## Usage

### Add a Game

```bash
cascadia add-game
```

Interactively records a completed game, including players, wildlife scores, habitat scores, landmarks, and notes.

### View the Leaderboard

```bash
cascadia leaderboard
```

Displays the highest scores recorded across all games.

### View Player Statistics

```bash
cascadia player-stats "Margot Nissen"
```

Displays:

- Games played
- Wins
- Win rate
- Average score
- Highest score
- Lowest score

### View Wildlife Statistics

```bash
cascadia animal-stats
```

Shows the average and highest score for each wildlife category.

### View Landmark Statistics

```bash
cascadia landmark-stats
```

Displays how often each landmark card has been used and its average score.

### View Category Leaders

```bash
cascadia category-stats
```

Shows which player has the highest average score in each scoring category.

### View Best Games

```bash
cascadia best-games
```

Displays the highest-scoring games ever recorded.

### Compare Two Players

```bash
cascadia rivalry "Margot Nissen" "Alex Smith"
```

Shows the number of games played together, wins for each player, and the average margin of victory.

### Export Data

```bash
cascadia export-csv
```

or

```bash
cascadia export-csv --filename scores.csv
```

Exports all recorded games to a CSV file containing detailed scoring information, wildlife scoring cards, habitat scores, landmark data, and game notes.

## Why I Built This

I regularly play Cascadia with friends and wanted a better way to keep track of our games over time. While the game includes scorepads, they only record final scores and are difficult to analyze later. Cascadia Tracker provides a permanent record of each game and makes it easy to compare players, identify scoring trends, and analyze how different wildlife scoring cards and landmark combinations affect gameplay.
