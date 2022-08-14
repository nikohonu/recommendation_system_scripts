#!/bin/python
import json
import pathlib
import random
import time

import requests

with pathlib.Path('steam_ids.json').open() as data_file:
    steam_ids = json.load(data_file)
    random.shuffle(steam_ids)

for steam_id in steam_ids:
    response = requests.get(f'http://127.0.0.1:5000/steam/get-profile/{steam_id}')
    try:
        print(response.url)
        profile = response.json()
        response = requests.post(
            'http://127.0.0.1:5000/auth/register',
            {'username': profile['name'],
             'password': '42774277', 'steam_profile_url': profile['url']})
        print(response)
        response = requests.get(
            f'http://127.0.0.1:5000/steam/get-profile-apps/{profile["id"]}')
        print(response)
        time.sleep(3)
    except json.decoder.JSONDecodeError as error:
        print(f"Error: {error}")
