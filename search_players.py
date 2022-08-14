'''Script for getting player steam id with public game list and save it to
user.json'''
import json
import pathlib
import random
import time

import requests

START = 76561198083927293
END = 76561198899999999
with pathlib.Path('steam_ids.json').open() as data_file:
    steam_ids = set(json.load(data_file))
while len(steam_ids) < 1300:
    steam_id = random.randrange(START, END)
    time.sleep(4)
    try:
        url = f"http://127.0.0.1:5001/get-playtime/{steam_id}"
        print(url, len(steam_ids))
        result = requests.get(url)
        result = result.json()
        steam_ids.add(steam_id)
        with pathlib.Path('steam_ids.json').open('w') as data_file:
            json.dump(list(steam_ids), data_file)
        print('ok')
    except json.decoder.JSONDecodeError:
        continue
