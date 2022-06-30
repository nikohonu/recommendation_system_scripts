'''Generate table based on players' data'''
import json
from pathlib import Path

import pandas as pd
import requests

from games import Games
from players import Players


class PlayerTable:
    def __init__(self):
        self._table = []

    def add_player(self, player_name, playtime):
        self._table.append({'player_name': player_name} | playtime)

    def remove_rare_games(self, game_table):
        game_table.calc()
        for user in self._table:
            keys = list(user.keys())[1:]
            for key in keys:
                if not game_table.have_game(key):
                    del user[key]

    def save(self):
        df = pd.DataFrame.from_dict(self._table)
        df.to_csv(r'players.csv', index=False, header=True)


def main():
    with Path("steam_ids.json").open(encoding="UTF-8") as source:
        steam_ids = json.load(source)
    games = Games(steam_ids)
    players = Players(steam_ids)
    games.save_to_csv()


if __name__ == '__main__':
    main()
