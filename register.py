#!/bin/python
import argparse
import json
import pathlib
import profile
import random
import time
from urllib import response

import requests

START = 76561198083927293
END = 76561198899999999


def check_user(steam_id):  # check if user exist or have a least 1 game on account
    response = requests.get(
        f'http://127.0.0.1:5000/steam/check-profile/{steam_id}')
    return response.status_code != 404


def register(steam_id):
    response = requests.get(
        f'http://127.0.0.1:5000/steam/get-player-summary/{steam_id}')
    if response.status_code != 404:
        player = response.json()
        name = player['personaname']
        profile_url = player['profileurl']
        response = requests.post(
            'http://127.0.0.1:5000/auth/register',
            {'username': name,
             'password': '42774277', 'steam_profile_url': profile_url})
        response = requests.get(
            f'http://127.0.0.1:5000/user/{name}/games')
        if not check_user(steam_id):
            response = requests.post(
                'http://127.0.0.1:5000/auth/delete',
                {'username': name, 'password': '42774277'})
        else:
            return True
    return False


# def find_new_user():
#     pass


parser = argparse.ArgumentParser(
    description='Register new account for Game List Site.')
parser.add_argument('count', type=int, help='count of accounts')
args = parser.parse_args()

print(args.count)

with pathlib.Path('steam_ids.json').open() as data_file:
    steam_ids = json.load(data_file)
i = 1
bad_steam_ids = []
print(len(steam_ids))
for steam_id in steam_ids:
    if check_user(steam_id):
        i += 1
    elif register(steam_id):
        i += 1
    else:
        bad_steam_ids.append(steam_id)
    if i > args.count:
        break
    print(i)
for steam_id in bad_steam_ids:
    steam_ids.remove(steam_id)
with pathlib.Path('steam_ids.json').open('w') as data_file:
    json.dump(list(steam_ids), data_file)
