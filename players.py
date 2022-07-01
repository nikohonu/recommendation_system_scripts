import json
from pathlib import Path

import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

from games import Games

# cosine_similarity([[1, 0, -1]], [[-1,-1, 0]])


class Game:
    def __init__(self, game_id, game_name, playtime):
        self.id = game_id
        self.name = game_name
        self.playtime = playtime

    @property
    def __dict__(self):
        return {self.name: self.playtime}


class Player:
    def __init__(self, player_id, player_name):
        self.id = player_id
        self.name = player_name
        self.games = []

    def add_game(self, game_id, game_name, playtime):
        self.games.append(Game(game_id, game_name, playtime))

    @property
    def __dict__(self):
        result = {'name': self.name}
        for game in self.games:
            result |= game.__dict__
        return result


class Players:
    def __init__(self, steam_ids, games: Games):
        self.players = []
        self.steam_ids = steam_ids
        self.games = games
        i = 0
        steam_ids_count = len(self.steam_ids)
        for steam_id in self.steam_ids:
            i += 1
            try:
                if i % 100 == 0:
                    print(f'Process user {i}/{steam_ids_count}')
                url = f"http://127.0.0.1:5000/get-player/{steam_id}"
                result = requests.get(url)
                player_data = result.json()
                player = Player(player_data['id'], player_data['name'])
                url = f"http://127.0.0.1:5000/get-playtime/{steam_id}"
                result = requests.get(url)
                playtime = result.json()
                for pt in playtime:
                    min_pt = min((pt['minutes'] / 60) / 10, 1)
                    if self.games.have(pt['game_id']) and \
                            pt['minutes'] >= min_pt:
                        player.add_game(
                            pt['game_id'],
                            pt['game_name'],
                            pt['minutes'] / 60)
                self.players.append(player)
            except requests.exceptions.JSONDecodeError:
                print(steam_id)
        self.normalize()

    def normalize(self):
        for player in self.players:
            for game in player.games:
                # X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
                # X_scaled = X_std * (max - min) + min
                pt = game.playtime
                global_game = self.games.get_game(game.id)
                max_pt = global_game.max_playtime
                min_pt = global_game.min_playtime
                median_pt = global_game.median_playtime
                if pt > median_pt:
                    pt = (pt - median_pt) / (median_pt * 3 - median_pt)
                    pt = pt * (1 - 0) + 0
                    game.playtime = min(pt, 1)
                else:
                    pt = (pt - 0) / (median_pt - 0)
                    pt = pt * (0 + 1) + -1
                    game.playtime = pt

    def save_to_csv(self):
        df = pd.DataFrame.from_dict(
            [player.__dict__ for player in self.players])
        df.to_csv(r'players.csv', index=False, header=True)
