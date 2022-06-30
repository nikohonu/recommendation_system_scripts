import json
from pathlib import Path

import pandas as pd
import requests


class Game:
    def __init__(self, game_id, game_name, playtime):
        self.id = game_id
        self.game_name = game_name
        self.playtime = playtime


class Player:
    def __init__(self, player_id, player_name):
        self.id = player_id
        self.name = player_name
        self.games = []


class Players:
    def __init__(self, steam_ids, update=False):
        self.players = []
        self.steam_ids = steam_ids
        if update or not Path('players.json').exists():
            self._update()
        else:
            self._load()

    def _update(self):
        i = 0
        steam_ids_count = len(self.steam_ids)
        for steam_id in self.steam_ids:
            i += 1
            try:
                print(f'Process {i}/{steam_ids_count}')
                url = f"http://127.0.0.1:5000/get-player/{steam_id}"
                result = requests.get(url)
                player = result.json()
                # print(player)
            except requests.exceptions.JSONDecodeError:
                print(steam_id)
