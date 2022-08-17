#!/bin/python
import json
import pathlib
import random
import time
from urllib import response

import requests

START = 76561198083927293
END = 76561198899999999

with pathlib.Path('steam_ids.json').open() as data_file:
    steam_ids = json.load(data_file)

# check is steam_ids is registered
i = 0
for steam_id in steam_ids:
    i += 1
    if i == 150:
        break
    response = requests.get(
        f'http://127.0.0.1:5000/steam/check-profile/{steam_id}')
    if response.status_code != 404:
        print(response.text)
    else:
        response = requests.get(
            f'http://127.0.0.1:5000/steam/get-profile/{steam_id}')
        if response.status_code:
            print(response.text)
            profile = response.json()
        response = requests.post(
            'http://127.0.0.1:5000/auth/register',
            {'username': profile['name'],
             'password': '42774277', 'steam_profile_url': profile['url']})
        response = requests.get(
            f'http://127.0.0.1:5000/user/{profile["name"]}')
        response = requests.get(
            f'http://127.0.0.1:5000/user/{profile["name"]}/games')
    response = requests.get(
        f'http://127.0.0.1:5000/steam/check-profile/{steam_id}')
    if response.status_code == 404:
        response = requests.post(
            'http://127.0.0.1:5000/auth/delete',
            {'username': profile['name'], 'password': '42774277'})
        i -= 1

        # for steam_id in steam_ids:
        #     try:
        #         print(response)
        #     except requests.exceptions.ConnectionError as error:
        #         print(f"Error: {error}")
        #         time.sleep(60)
        #     except requests.exceptions.JSONDecodeError:
        #         print(f"Error: {error}")
        #         pass
