# Cascadia Results Tracker
DSC 190 Final Project

This program enters results for the board game Cascadia by Randy Flynn. It records detailed scoring breakdowns of games for board game nerds. It helps players track long-term statitiscs like highest scoring game, win rates, and head-to-head performances.

## Usage
To log a new game, you can type "cascadia add-game" which interactively records a completed game. You can also view the leaderboard, view individual player's statistics, wildlife statistics, category leaders, and best games. All the data is stored in a JSON file and you can use "cascadia export-csv --filename scores.csv" to transform it into a CSV file and conduct further analysis in R, python, or excel.
