import json
import statistics
from pathlib import Path

import pandas as pd
import requests


class Game:
    def __init__(self, game_id, game_name):
        self.id = game_id
        self.name = game_name
        self.playtime = []

    @classmethod
    def from_dict(cls, data: dict):
        game = cls(data['id'], data['name'])
        game.playtime = data['playtime']
        return game

    @property
    def total_playtime(self):
        return sum(self.playtime)

    @property
    def mean_playtime(self):
        return statistics.mean(self.playtime)

    @property
    def median_playtime(self):
        return statistics.median(self.playtime)

    @property
    def high_median_playtime(self):
        return statistics.median([pt for pt in self.playtime
                                  if pt >= self.median_playtime])

    @property
    def max_playtime(self):
        return max(self.playtime)

    @property
    def min_playtime(self):
        return min(self.playtime)

    @property
    def player_count(self):
        return len(self.playtime)

    @property
    def row(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_playtime': self.total_playtime,
            'mean_playtime': self.mean_playtime,
            'median_playtime': self.median_playtime,
            'high_median_playtime': self.high_median_playtime,
            'max_playtime': self.max_playtime,
            'min_playtime': self.min_playtime,
            'player_count': self.player_count,
        }

    def add_playtime(self, hours):
        self.playtime.append(hours)


class Games:
    def __init__(self, steam_ids, update=False):
        self.games = []
        self.steam_ids = steam_ids
        if update or not Path('games.json').exists():
            self._update()
        else:
            self._load()

    def have(self, game_id):
        for game in self.games:
            if game.id == game_id:
                return True
        return False

    def _get_or_add_game(self, game_id, game_name):
        for game in self.games:
            if game.id == game_id:
                return game
        self.games.append(Game(game_id, game_name))
        return self.games[-1]

    def get_game(self, game_id):
        for game in self.games:
            if game.id == game_id:
                return game

    def _update(self):
        i = 0
        steam_ids_count = len(self.steam_ids)
        for steam_id in self.steam_ids:
            i += 1
            if i % 100 == 0:
                print(f'Process games {i}/{steam_ids_count}')
            url = f'http://127.0.0.1:5000/get-playtime/{steam_id}'
            result = requests.get(url)
            playtime = result.json()
            for pt in playtime:
                game = self._get_or_add_game(pt['game_id'], pt['game_name'])
                game.add_playtime(pt['minutes'] / 60)
        self.games = [game for game in self.games if game.player_count >= 5]

    @property
    def __dict__(self):
        return [game.__dict__ for game in self.games]

    def _load(self):
        with Path('games.json').open() as file:
            games = json.load(file)
        for game in games:
            self.games.append(Game.from_dict(game))

    def __del__(self):
        if self.games:
            with Path("games.json").open('w') as file:
                json.dump(self.__dict__, file)

    def save_to_csv(self):
        df = pd.DataFrame.from_dict([game.row for game in self.games])
        df.to_csv(r'games.csv', index=False, header=True)
