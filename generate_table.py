'''Generate table based on players' data'''
import json
from pathlib import Path

import pandas as pd
import requests


class GameTable:
    def __init__(self):
        self._table = []

    def get_or_add_game(self, game_id, game_name):
        for game in self._table:
            if game['game_id'] == game_id:
                return game
        self._table.append({
            'game_id': game_id,
            'game_name': game_name,
            'playtime': 0,
            'avg_playtime': 0,
            'max_playtime': 0,
            'min_playtime': 10000,
            'player_count': 0, })
        return self._table[-1]

    def calc(self):
        new_table = []
        for game in self._table:
            game['avg_playtime'] = game['playtime'] / game['player_count']
            if game['player_count'] >= 5:
                new_table.append(game)
        self._table = new_table

    def have_game(self, name):
        for game in self._table:
            if game['game_name'] == name:
                return True
        return False

    def save(self):
        self.calc()
        df = pd.DataFrame.from_dict(self._table)
        df.to_csv(r'games.csv', index=False, header=True)


class PlayerTable:
    def __init__(self):
        self._table = []

    def add_player(self, player_name, playtime):
        self._table.append({'player_name': player_name} | playtime)

    def remove_rare_games(self, game_table: GameTable):
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
    '''Entry point of the script'''
    players = []
    game_table = GameTable()
    player_table = PlayerTable()
    with Path("users.json").open(encoding="UTF-8") as source:
        players = json.load(source)
    for steam_id in players:
        try:
            url = f"http://127.0.0.1:5000/get-player/{steam_id}"
            result = requests.get(url)
            player = result.json()
            url = f"http://127.0.0.1:5000/get-playtime/{steam_id}"
            result = requests.get(url)
            playtime = result.json()
            player_playtime = {}
            for pt in playtime:
                game = game_table.get_or_add_game(
                    pt['game_id'], pt['game_name'])
                pt_hours = pt['minutes'] / 60
                player_playtime[pt['game_name']] = pt_hours
                game['playtime'] += pt_hours
                game['max_playtime'] = max(game['max_playtime'], pt_hours)
                game['min_playtime'] = min(game['min_playtime'], pt_hours)
                game['player_count'] += 1
            player_table.add_player(player['name'], player_playtime)
        except requests.exceptions.JSONDecodeError:
            print(steam_id)
    player_table.remove_rare_games(game_table)
    game_table.save()
    player_table.save()


if __name__ == '__main__':
    main()
