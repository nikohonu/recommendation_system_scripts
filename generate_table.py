'''Generate table based on players' data'''
import json
from pathlib import Path

from games import Games
from players import Players


def main():
    with Path("steam_ids.json").open(encoding="UTF-8") as source:
        steam_ids = json.load(source)
    games = Games(steam_ids, True)
    games.save_to_csv()
    players = Players(steam_ids, games)
    players.save_to_csv()
    players.save_sim_to_csv()
    players.get_recommendations('andinoriel')


if __name__ == '__main__':
    main()
