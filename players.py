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
    def __init__(self, player_id, player_name, all_games):
        self.id = player_id
        self.name = player_name
        self.games = []
        self.similarities = {}
        self.vector = []
        self.all_games = all_games

    def add_game(self, game_id, game_name, playtime):
        self.games.append(Game(game_id, game_name, playtime))

    def get_playtime(self, game_id):
        for game in self.games:
            if game.id == game_id:
                return game.playtime
        return 0

    def have_game(self, game_id):
        for game in self.games:
            if game.id == game_id:
                return True
        return False

    def get_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def calc_vector(self):
        for game in self.all_games:
            self.vector.append(self.get_playtime(game.id))

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
                player = Player(player_data['id'],
                                player_data['name'], self.games.games)
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
                if len(player.games) >= 5:
                    self.players.append(player)
            except requests.exceptions.JSONDecodeError:
                print(steam_id)
        self.normalize()
        self.sim_table = self.calc_similarities()

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

    def calc_similarities(self):
        # for a in self.players:
        # for b in self.players:
        # a.add_similarity(self.games, b)
        table = []
        for player in self.players:
            player.calc_vector()
            table.append(player.vector)
        table = cosine_similarity(table)
        sim_table = []
        for row, a in zip(table, self.players):
            tmp = {}
            new_row = {'name': a.name}
            for num, b in zip(row, self.players):
                new_row |= {b.name: num}
                tmp |= {b.name: num}
            sim_table.append(new_row)
            a.similarities = tmp
        return sim_table

    def save_to_csv(self):
        df = pd.DataFrame.from_dict(
            [player.__dict__ for player in self.players])
        df.to_csv(r'players.csv', index=False, header=True)

    def save_sim_to_csv(self):
        # data = []
        # for player in self.players:
        # data.append({'name': player.name} | player.similarities)
        df = pd.DataFrame.from_dict(self.sim_table)
        df.to_csv(r'players_sim.csv', index=False, header=True)

    def get_player(self, player_name):
        for player in self.players:
            if player.name == player_name:
                return player

    def get_recommendations(self, player_name):
        player = self.get_player(player_name)
        g0 = set()  # games that player don't play
        g1 = set()  # games that simular user play
        player.similarities = dict(
            sorted(player.similarities.items(), key=lambda item: item[1], reverse=True))
        similarities = {}
        i = 0
        for p in player.similarities:
            if p != player.name and i < 10:
                similarities[p] = player.similarities[p]
                i += 1

        for p in similarities:
            p = self.get_player(p)
            g1 |= set([game.name for game in p.games])
        for g in self.games.games:
            if player.have_game(g.id) == 0:
                g0.add(g.name)

        print(similarities)
        g2 = g0 & g1
        r = []
        for game_name in g2:
            total = 0
            count = 0
            for s in similarities:
                p = self.get_player(s)
                game = p.get_game(game_name)
                if game:
                    total += game.playtime * similarities[s]
                    count += 1
            r.append({'name': game_name, 'score': total/count, 'count': count})
        df = pd.DataFrame.from_dict(r)
        df.to_csv(r'r.csv', index=False, header=True)
